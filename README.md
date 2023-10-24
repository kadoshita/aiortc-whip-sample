# aiortc-whip-sample

aiortcを使って、WebRTCのMediaStreamを受信するWHIPサーバーのサンプル

## 利用方法

### セットアップ

```sh
$ git clone git@github.com:kadoshita/aiortc-whip-sample.git
$ cd aiortc-whip-sample
$ python -m venv .
$ source bin/activate
$ python -m pip install -r requirements.txt
$ patch -d ./lib/path/to/aiortc/ -p1 < ./patch/set_cipher_list.patch # 重要!!
$ cd src
$ python main.py
```

### OBSの設定

1. 設定→配信を開く
2. サービスとして「WHIP」を選択する
3. サーバーのアドレスとして「[http://localhost:8080/whip](http://localhost:8080/whip)」を設定する
4. OKを押して閉じる

- 「配信開始」ボタンを押せば、WHIPでの配信が始まります。

## パッチについて

- `patch/set_cipher_list.patch` で、aiortcが利用する暗号スイートを変更しています。これは、以下の理由によるものです。
    - OBSでは、WebRTCのライブラリとしてlibdatachannelを利用しており、OBSで利用されているlibdatachannelはMbed TLSを利用する設定でビルドされています。
    - Mbed TLSは、v3.5.0の時点で、Client Helloのフラグメンテーションをサポートしていません。
      - https://github.com/Mbed-TLS/mbedtls/blob/v3.5.0/library/ssl_tls12_server.c#L1085
    - そのため、利用可能な暗号の数が多い場合、Client Helloのサイズが大きくなり、フラグメンテーションが発生し、接続時にエラーとなります。
    - これを防ぐために、暗号スイートを明示的に設定し、フラグメンテーションが発生しないサイズに抑えています。
    - なお、libdatachannelを、OpenSSLを利用する設定でビルドした場合は、この問題が発生しないことを確認しています。

