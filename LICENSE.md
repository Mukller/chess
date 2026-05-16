# MIT License

Copyright (c) 2026 Mukller

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Third-party software

This project bundles or depends on the following third-party components, each
released under its own license. Their licenses apply to the respective parts
of the project:

| Component        | License                                                        |
| ---------------- | -------------------------------------------------------------- |
| Stockfish        | [GPL-3.0](https://github.com/official-stockfish/Stockfish/blob/master/Copying.txt) |
| python-chess     | [GPL-3.0](https://github.com/niklasf/python-chess/blob/master/LICENSE.txt) |
| FastAPI          | MIT                                                            |
| aiogram          | MIT                                                            |
| Redis (server)   | RSALv2 / SSPLv1 / AGPLv3 (см. дистрибутив)                     |
| React            | MIT                                                            |
| react-chessboard | MIT                                                            |
| chess.js         | BSD-2-Clause                                                   |
| TailwindCSS      | MIT                                                            |
| Vite             | MIT                                                            |
| Nginx            | BSD-2-Clause                                                   |

> ⚠️ **Stockfish** распространяется под **GPL-3.0**. Если вы дистрибутируете
> бинарник Stockfish вместе с проектом, вы обязаны соблюдать условия GPL-3.0
> (предоставление исходников, копии лицензии и т.д.). В этом репозитории
> Stockfish устанавливается из официальных Debian/Ubuntu пакетов внутри Docker
> образа — пользователь сам берёт на себя обязательства GPL при дистрибуции
> собранного образа.
