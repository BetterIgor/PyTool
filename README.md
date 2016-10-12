

FieldsFormatter

达到的目的：找出最完整的字段信息，并将不同资源中（国际化：中文，英文等文件）字段的位置统一。

使用场景：在项目开发阶段，开发人员可能会对字段国际化的遗漏（导致项目不完整），或者字段位置不同步（codeReview时不方便）。

使用说明：准备chinese.xml，english.xml,fanti.xml
  如：
      editFile = parseFile("chinese.xml") # 表示：将要修改的文件
      referFile = parseFile("english.xml") # 表示：参考的文件
      首先将chinese.xml备份，然后将english.xml中有而chinese.xml没有的字段一同写入到all.xml文件中（此时该文件中的字段是最完整的），
      然后将all.xml备份a，并对应将english.xml中字段的值在a中替换（中文的值修改为英文），最后输出新的chinese.xml,english.xml文件(此时的文件，
      即可达到字段的同步（不遗漏，位置对应）)。
      以此类推，可以实现不同语言中字段的同步。
