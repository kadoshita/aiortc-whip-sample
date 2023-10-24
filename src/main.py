import logging
from aiohttp import web
from aiohttp_middlewares import cors_middleware
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaRecorder

logger = logging.getLogger('whip')

class WHIP:
    def __init__(self):
        self._pc = None
        self._recorder = None

    async def whip(self, request):
        if request.content_type != 'application/sdp':
            return web.Response(status=400)
        if self._recorder is not None:
            return web.Response(status=400)
        if self._pc is not None:
            return web.Response(status=400)

        offerText = await request.text()

        logger.info(offerText)
        offer = RTCSessionDescription(sdp=offerText, type='offer')

        self._pc = RTCPeerConnection()

        # self.recorder = MediaBlackhole()
        self._recorder = MediaRecorder('output.mp4')

        @self._pc.on('iceconnectionstatechange')
        async def on_iceconnectionstatechange():
            logger.info('ICE connection state is %s', self._pc.iceConnectionState)
            if self._pc.iceConnectionState == 'failed':
                await self._pc.close()

        @self._pc.on('track')
        def on_track(track):
            logger.info('Track %s received', track.kind)

            self._recorder.addTrack(track)

            @track.on('ended')
            async def on_ended():
                logger.info('Track %s ended', track.kind)
                await self._recorder.stop()

        await self._pc.setRemoteDescription(offer)
        await self._recorder.start()

        answer = await self._pc.createAnswer()
        await self._pc.setLocalDescription(answer)

        logger.info(answer.sdp)

        return web.Response(
            status=201,
            content_type='application/sdp',
            headers={'Access-Control-Allow-Origin': '*', 'Access-Controll-Allow-Header': '*', 'Location': '/whip'},
            text=answer.sdp
        )

    async def stop_whip(self, request):
        if self._recorder:
            await self._recorder.stop()
            self._recorder = None
        if self._pc:
            await self._pc.close()
            self._pc = None

        return web.Response(status=200)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = web.Application(middlewares=[cors_middleware(allow_all=True)])
    whip = WHIP()
    app.router.add_post('/whip', whip.whip)
    app.router.add_delete('/whip', whip.stop_whip)

    web.run_app(app, port=8080, access_log=logger)
