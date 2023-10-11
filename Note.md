


## 打包

```
# 生成 spec (一次就可以了, 后续可以不用重复生成)
pyinstaller tomato.py -n 番茄时钟 --onefile --noconsole --noupx --clean
# 基于 spec 打包
pyinstaller 番茄时钟.spec
# -F 选项不要, 否则 makespec options not valid when a .spec file is given
```

### 关于音频打包

spec 修改 `datas=[('resource','resource')]`.
音频文件放在 resource 里.
同理, 有其他文件也可以放在这里.


## 问题
```
# 安装 playsound 可能失败, 先升级 wheel 试试 [python - Why is there an error when I try to install playsound module in VScode? - Stack Overflow](https://stackoverflow.com/questions/76078698/why-is-there-an-error-when-i-try-to-install-playsound-module-in-vscode)
pip3 install --upgrade wheel
pip3 install playsound
```
可能和音频素材有关系. ogg 转成 mp3 可以了. 但某些 mp3 也不行.
