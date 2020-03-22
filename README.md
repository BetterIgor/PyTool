
<pre>
FieldsFormatter.py
</pre>
主要是用来格式化资源文件（如：string），适用于字段不统一的国际化资源，通过打补丁的方式保证字段的完整性。然后将文件国际化。避免了人工手动的繁琐，方便codeReview也提高了研发效率。

达到的目的：找出最完整的字段信息，并将不同资源中（国际化：中文，英文等资源文件）字段的位置统一。

使用场景：在项目开发阶段，开发人员可能会对字段国际化的遗漏（导致项目不完整），或者字段位置不同步（codeReview时不方便）。

使用说明：准备chinese.xml，english.xml,fanti.xml
  如：
      editFile = parseFile("chinese.xml") # 表示：将要修改的文件
      referFile = parseFile("english.xml") # 表示：参考的文件
      首先将chinese.xml备份，然后将english.xml中有而chinese.xml没有的字段一同写入到all.xml文件中（此时该文件中的字段是最完整的），
      然后将all.xml备份a，并对应将english.xml中字段的值在a中替换（中文的值修改为英文），最后输出新的chinese.xml,english.xml文件(此时的文件，
      即可达到字段的同步（不遗漏，位置对应）)。
      以此类推，可以实现不同语言中字段的同步。

<pre>
SMParser.py
</pre>
主要用力整理StrictMode生成的日志包括合并、去重、排序等。
可以在项目中使用StrictMode，用adb logcat -s StrictMode  > log.txt生成日志，然后放置与SMParser.py同级目录并运行。
StrictMode示例：
public class StrictModeManager {
    public static void init() {
        StrictMode.setThreadPolicy(new StrictMode.ThreadPolicy.Builder()
                .detectAll()
                .penaltyLog()
                .build());
        StrictMode.setVmPolicy(new StrictMode.VmPolicy.Builder()
                .detectAll()
                .penaltyLog()
                .build());
    }
}

<pre>
parser.py
</pre>
按照excel中的列（可一对多）归并为xml中的结构。input是实例文件，output是归并结果（可能需要手动导入xlrd库：pip3 install xlrd）


<pre>
night-mode.py
</pre>
用来统一颜色，将定义相同颜色值的color引用到相同的color，方便夜间模式的修改，也方便后续的维护。使用方法：将apk反编译拿到colors，在同级目录运行即可


<pre>
layoutParser.py 
</pre>
遍历Android中的所有布局的层级并排序输出（然后将层级到的布局使用约束布局去优化，参数需要指定layout的目录。如：python3 LayoutParser.py /Users/igor/workspace/app/res/layout


<pre>
EyeLogParser.py
</pre>
用来解析GodEye生产出来的日志，可以展示一段时间内被测的情况从而进一步优化。通过指定apk的路径得到大小，然后反编译后用LayoutParser得到应用的布局层级。其中BASE_INFO的数据GodEye没有，是从app中输出的。最终展示信息如:
<pre>
{
    "===================基本信息===================":"",
    "包名":"x.x.x",
    "版本名":"6.391.0.debug",
    "版本号":179,
    "最小版本号":21,
    "目标版本号":26,
    "系统版本":"7.0",
    "设备型号":"Android Google Nexus 5X",
    "测试时长":"00:40:25",
    "测试页面":"44个",
    "===================优化指标===================":"",
    "启动":"类型: cold, 最长耗时: 24350ms, 平均耗时: 13552.0ms ",
    "流畅度":"平均值：28.29帧/秒",
    "内存泄漏":"18次",
    "耗电量":"1%",
    "CPU":"最大使用率：30.36%, 平均使用率：18.92%",
    "HEAP":"最大占用：262144KB, 平均占用：256589.76KB",
    "RAM":"最大占用：710140KB, 平均占用：479022.93KB",
    "生命周期":"最长耗时: 137ms, 平均耗时: 15.99ms",
    "APK大小":"31481.38KB",
    "布局层级":"最大值：9, 平均值：2.69"
}
</pre>
