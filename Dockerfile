# uv は FROM に書いておくと Dependabot が更新してくれる
FROM ghcr.io/astral-sh/uv:0.13.1 AS uv

FROM python:3.15-slim-trixie AS base

# libtk8.6: tkinter, fonts-ipafont-gothic: 日本語の表示, xvfb: 画面のない仮想ディスプレイ
RUN apt-get update \
    && apt-get install -y --no-install-recommends libtk8.6 fonts-ipafont-gothic xvfb \
    && rm -rf /var/lib/apt/lists/*
COPY --from=uv /uv /bin/uv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH=/opt/venv/bin:$PATH
RUN useradd --create-home --uid 1000 app
# Xvfb は root 以外だとこのフォルダを作れない
RUN mkdir -m 1777 /tmp/.X11-unix
WORKDIR /app
COPY pyproject.toml uv.lock ./

FROM base AS dev
# xauth: テストを仮想ディスプレイで動かす xvfb-run に要る
RUN apt-get update \
    && apt-get install -y --no-install-recommends xauth \
    && rm -rf /var/lib/apt/lists/*
RUN uv sync --locked
# マウントしたフォルダのユーザーが違っても動くように、キャッシュは書かない
ENV RUFF_NO_CACHE=true \
    PYTEST_ADDOPTS="-p no:cacheprovider" \
    PYTHONDONTWRITEBYTECODE=1
COPY . .
USER app
CMD ["sh", "-c", "ruff check && ruff format --check && xvfb-run -a pytest"]

FROM base AS app
# x11vnc + noVNC: 仮想ディスプレイをブラウザで見る
# (Debian の novnc パッケージは nodejs ごと入って重いので、noVNC は公式リリースの静的ファイルを使う)
# noVNC は Dependabot が更新できないので、URL と checksum は手で更新する
RUN apt-get update \
    && apt-get install -y --no-install-recommends x11vnc websockify \
    && rm -rf /var/lib/apt/lists/*
ADD --checksum=sha256:b1003a11b6e6e8d8f7f5e5586daae7f8ca651d8aee0aa155ff9ac841c48f52c6 \
    https://github.com/novnc/noVNC/archive/refs/tags/v1.7.0.tar.gz /tmp/novnc.tar.gz
RUN mkdir /opt/novnc \
    && tar xzf /tmp/novnc.tar.gz -C /opt/novnc --strip-components=1 \
    && rm /tmp/novnc.tar.gz
RUN uv sync --locked --no-dev
COPY MyDiceRoll.py ./
COPY docker/start.sh ./docker/start.sh
USER app
EXPOSE 6080
# noVNC のページと、その先の VNC サーバー (x11vnc) の両方が動いているか
HEALTHCHECK --interval=30s --start-period=20s --start-interval=1s CMD python -c "\
import socket, urllib.request; \
urllib.request.urlopen('http://localhost:6080/vnc.html'); \
assert socket.create_connection(('localhost', 5900), 2).recv(3) == b'RFB'"
CMD ["sh", "/app/docker/start.sh"]
