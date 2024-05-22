# TODO Thumbs.db 这些垃圾数据要在同步bat里面屏蔽，不要进入logfile里
# TODO 653B里的否决设置是这样的：/.AppleDB/.AppleDouble/.AppleDesktop/:2eDS_Store/Network Trash Folder/Temporary
#  Items/TheVolumeSettingsFolder/.@__thumb/.@__desc/:2e*/.@__qini/.Qsync/.@upload_cache/.qsync/.qsync_sn/.@qsys
#  /.streams/.digest/.DS_Store/Thumbs.db/  # Thumbs.db 这类垃圾要在同步里面屏蔽
# TODO 算法1
# 将所有的目录进行Rename,同时将新旧名字放进一个字典，key value
# 将所有的文件进行Rename(这里判断最后一位是否短名了? ,是短名跳过，是长名，，， 判断BaseDIR是否在以上的改目录名之内，在的话先格式化一下改后的名字
# 缩短的算法: 1。 要判断是否全角/半角，，， 计算总体长度？ 还是暴力直接中英文 一起来 84个字符上限，，？。。。 2。 空格。。。删掉？。。。  83*3+4+2 = 255
# TODO 算法2
# 按照FastCopy.log的列表顺序，从上至下,一个个的rename，凡是文件的rename要反溯其BaseDir是否和上一个rename的文件夹同名，如果是的化，要改baseDir否则rename会失败。
# _rename.log 字典日志，，，存哪儿？？？ 。。。 同级目录。。。 多个rename， Append 进去?... 加上时间。

import os
import logging


# Kenny@20211022 日志初始化函数,,,增加复用率
def init_logger(str_dir):
    # 初始化 Logging,  获取logger对象,取名RENAME_LONG_PATH
    logger = logging.getLogger("RENAME_LONG_PATH")
    # 输出DEBUG及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.DEBUG)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(str_dir + "_long_path.log")
    handler.setLevel(logging.INFO)  # 过滤 低于这个级别的不写文件
    # 生成并设置文件日志格式，其中name为上面设置的mylog
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M")
    handler.setFormatter(formatter)
    # 获取流句柄并设置日志级别，第二层过滤
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)  # 过滤 低于这个级别的不进入console
    # 为logger对象添加句柄
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger


# 这里处理缩短的时候需要注意是否为文件名还是目录，如果目录，不保留后缀名，如果是文件的话，要保留最后一个.号后面的后缀名再拼接回去
# 这里 ~0是裁剪文件名后的初始序号，从0开始，+1 ，9之后用大写字母，一共36个同名文件名序号池，应该够用了
# Kenny@20211022 这个专门处理文件名改名
def rename_file(str_long_path):
    if not os.path.exists(str_long_path):
        return
    int_last_slash = str_long_path.rfind("/")
    str_basedir = str_long_path[0:int_last_slash + 1]
    str_long_name = str_long_path[int_last_slash + 1:]
    if len(str_long_name) < 85:  # Kenny@20211027 本身就是短文件名的可以直接跳过，进入日志是因为上级目录太长
        return

    # Kenny@20211022 一个叫rename的logger被初始化
    log_rename_file = init_logger(str_basedir)

    # if os.path.isfile(str_long_path):  # Kenny@20211022 文件名比较麻烦一些
    # 取后缀名临存。  常见的后缀最长4个字符，超过6个字符 视为非后缀名，直接采用文件夹的方式截取
    int_last_dot = str_long_name.rfind(".")
    str_ext = str_long_name[int_last_dot:]
    int_right_name_org = 84 - len(str_ext)
    str_file_base_name = str_long_name[0:int_last_dot]
    # print(str_file_base_name)
    str_right_name_org = str_file_base_name.replace(
        " ", "")[0:int_right_name_org] + "~"

    i = 0
    while True:  # Kenny@20211022 这里模拟 do...while
        str_right_name = str_right_name_org + str(i) + str_ext
        str_right_path = str_basedir + str_right_name
        i += 1
        if not os.path.exists(str_right_path):  # 判断文件是否有重名的，有的话，尾标递增
            break

    os.rename(str_long_path, str_right_path)  # Kenny@20211022 临时注释
    log_rename_file.info(str_long_name + "\n    ========>> " +
                         str_right_name)  # 换行后4个空格

    # Kenny@20211027 必须这样释放log的handlers，否则在执行重命名路径或删除日志文件的时候会出现文件在使用中的权限问题。
    log_handlers = log_rename_file.handlers[:]
    for handler in log_handlers:
        handler.close()
        log_rename_file.removeHandler(handler)


# 这里处理缩短的时候需要注意是否为文件名还是目录，如果目录，不保留后缀名，如果是文件的话，要保留最后一个.号后面的后缀名再拼接回去
# TODO [未完成] 这里 ~0是裁剪文件名后的初始序号，从0开始，+1 ，9之后用大写字母，一共36个同名文件名序号池，应该够用了
# Kenny@20211022 解绑，分两个函数，这个专门处理文件夹的改名
# Kenny@20211025 这里需要返回更新后的基准 path 。。。  //否则 下面的 文件的基础文件夹已经被改名了。。。会出错
def rename_path(str_long_path):
    if not os.path.exists(str_long_path):
        return
    int_last_slash = str_long_path.rfind("/")
    str_basedir = str_long_path[0:int_last_slash + 1]
    str_long_name = str_long_path[int_last_slash + 1:]
    if len(str_long_name) < 85:  # Kenny@20211027 本身就是短文件名的可以直接跳过，进入日志是因为上级目录太长
        return

    # Kenny@20211022 一个叫rename的logger被初始化
    log_rename_path = init_logger(str_basedir)
    str_right_name_org = str_long_name.replace(" ", "")[0:84] + "~"

    i = 0
    while True:  # Kenny@20211025 这里模拟 do...while
        str_right_name = str_right_name_org + str(i)
        str_right_path = str_basedir + str_right_name
        i += 1
        if not os.path.exists(str_right_path):  # 判断文件是否有重名的，有的话，尾标递增
            break

    os.rename(str_long_path, str_right_path)  # Kenny@20211022 临时注释
    log_rename_path.info(str_long_name + "\n    ========>> " +
                         str_right_name)  # 换行后4个空格

    log_handlers = log_rename_path.handlers[:]
    for handler in log_handlers:
        handler.close()
        log_rename_path.removeHandler(handler)


with open("./FastCopy.log") as f:
    content = f.read().splitlines()  # splitlines()这个函数可以将list里的换行符去掉,
    # content_rev = content.reverse()  # Kenny@20211025  这里用逆序先处理文件名，再上面是文件夹的。。。
    for item in reversed(content):
        # 按照算法2 ，一个个的历遍处理
        if (item.find(
                "CreateDirectory(The filename, directory name, or volume label syntax is incorrect.123)"
        ) >= 0):
            str_long_full_path = item.replace(
                "CreateDirectory(The filename, directory name, or volume label syntax is incorrect.123) : \\\\172.17.17.17\\shr",
                "/Volumes/shr$",
            )
            str_long_full_path = str_long_full_path.replace("\\", "/")
            print(str_long_full_path)
            rename_path(str_long_full_path)
        elif (item.find(
                "CreateFile(The filename, directory name, or volume label syntax is incorrect.123)"
        ) >= 0):
            str_long_full_file = item.replace(
                "CreateFile(The filename, directory name, or volume label syntax is incorrect.123) : \\\\172.17.17.17\\shr",
                "/Volumes/shr$",
            )
            str_long_full_file = str_long_full_file.replace("\\", "/")
            print(str_long_full_file)
            rename_file(str_long_full_file)