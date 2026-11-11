Name:		jsoup
Version:	1.24.1
Release:	2
Summary:	Java HTML parser
Group:		Development/Java
License:	MIT
URL:		https://jsoup.org/
Source0:	https://github.com/jhy/jsoup/archive/refs/tags/jsoup-%{version}.tar.gz#/jsoup-%{version}.tar.gz
Source1:	https://github.com/jhy/jsoup/archive/refs/tags/jsoup-1.23.2.tar.gz#/jsoup-1.23.2.tar.gz

BuildArch:	noarch
BuildRequires:	python
BuildRequires:	mvn(org.jspecify:jspecify)
BuildRequires:	mvn(com.google.re2j:re2j)
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
HTML parser. 1.24.1 adds an opt-in web query mode, parses processing
instructions, removes APIs that were scheduled for removal, and caps a
response body at 2 MB unless the caller raises the limit. The upstream
POM turns the default compile off, so this build replaces it with a
flat POM. The Java 11 HTTP client overrides are not compiled. RE2/J is
an optional runtime dependency used for linear-time selector regexes.
The build targets Java 8 and skips tests. The automatic module name is
org.jsoup. Gradle 9.9.1 strictly requests 1.23.2, so that jar is
installed beside %{version}. Its sources are the Java 8 tree only.

%prep
%autosetup -n jsoup-jsoup-%{version}
python - <<'PY'
import xml.etree.ElementTree as ET
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def tag(name):
    return "{" + NS + "}" + name

def add(parent, name, text):
    node = ET.SubElement(parent, tag(name))
    node.text = text
    return node

root = ET.Element(tag("project"))
add(root, "modelVersion", "4.0.0")
add(root, "groupId", "org.jsoup")
add(root, "artifactId", "jsoup")
add(root, "version", "%{version}")
add(root, "name", "jsoup Java HTML Parser")
props = ET.SubElement(root, tag("properties"))
add(props, "maven.compiler.release", "8")
deps = ET.SubElement(root, tag("dependencies"))
dep = ET.SubElement(deps, tag("dependency"))
add(dep, "groupId", "org.jspecify")
add(dep, "artifactId", "jspecify")
add(dep, "version", "1.0.0")
add(dep, "scope", "provided")
dep = ET.SubElement(deps, tag("dependency"))
add(dep, "groupId", "com.google.re2j")
add(dep, "artifactId", "re2j")
add(dep, "version", "1.8")
add(dep, "optional", "true")
ET.ElementTree(root).write("pom.xml", encoding="utf-8", xml_declaration=True)
text = open("pom.xml", encoding="utf-8").read()
for needle in (
    "<scope>provided</scope>",
    "<optional>true</optional>",
    "<artifactId>re2j</artifactId>",
    "<maven.compiler.release>8</maven.compiler.release>",
):
    if needle not in text:
        raise SystemExit("pom missing " + needle)
PY
%setup -q -T -D -a 1 -n jsoup-jsoup-%{version}
find jsoup-jsoup-1.23.2 \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete
rm -f jsoup-jsoup-1.23.2/pom.xml

%build -a
cat > manifest-addition <<'EOF'
Automatic-Module-Name: org.jsoup
EOF
jar ufm target/jsoup-%{version}.jar manifest-addition
java --module-path target/jsoup-%{version}.jar --describe-module org.jsoup | grep -q '^org.jsoup'
mkdir -p jsoup123/classes
find jsoup-jsoup-1.23.2/src/main/java -name '*.java' > jsoup123/sources.list
test -s jsoup123/sources.list
javac --release 8 -encoding UTF-8 -Xlint:-options \
	-cp %{_javadir}/jspecify.jar:%{_javadir}/re2j.jar \
	-d jsoup123/classes @jsoup123/sources.list
cat > jsoup123/manifest.mf << 'EOF'
Manifest-Version: 1.0
Automatic-Module-Name: org.jsoup

EOF
jar cfm jsoup123/jsoup.jar jsoup123/manifest.mf -C jsoup123/classes .
cat > jsoup123/jsoup.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.jsoup</groupId>
  <artifactId>jsoup</artifactId>
  <version>1.23.2</version>
  <name>jsoup Java HTML Parser</name>
  <description>Java HTML parser, Java 8 sources of the 1.23.2 tag.</description>
  <url>https://jsoup.org/</url>
  <licenses>
    <license>
      <name>MIT</name>
      <url>https://jsoup.org/license</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.jspecify</groupId>
      <artifactId>jspecify</artifactId>
      <version>1.0.0</version>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>com.google.re2j</groupId>
      <artifactId>re2j</artifactId>
      <version>1.8</version>
      <optional>true</optional>
    </dependency>
  </dependencies>
</project>
EOF

%install -p
sysjar install --buildroot %{buildroot} \
	--artifact jsoup123/jsoup.pom:jsoup123/jsoup.jar \
	--file-name jsoup-1.23.2 \
	--filelist .mfiles123
# %{version} owns jsoup.sysjar. 1.23.2 keeps a second index file.
/bin/mv %{buildroot}/usr/share/sysjar/index/org.jsoup/jsoup.sysjar \
	%{buildroot}/usr/share/sysjar/index/org.jsoup/jsoup-1.23.2.sysjar
sed -i 's|/usr/share/sysjar/index/org.jsoup/jsoup\.sysjar|/usr/share/sysjar/index/org.jsoup/jsoup-1.23.2.sysjar|' .mfiles123

%install -a
while IFS= read -r line; do
	grep -qxF -- "$line" .mfiles || printf '%s\n' "$line" >> .mfiles
done < .mfiles123

%check
cat > JsoupSmoke.java << 'EOF'
import org.jsoup.Jsoup;
public class JsoupSmoke {
	public static void main(String[] args) {
		String text = Jsoup.parse("<p>Hello</p>").selectFirst("p").text();
		if (!"Hello".equals(text)) {
			throw new AssertionError(text);
		}
		System.out.println(args[0] + " " + text);
	}
}
EOF
javac --release 8 -encoding UTF-8 -Xlint:-options \
	-cp "%{buildroot}%{_javadir}/jsoup.jar" \
	-d . JsoupSmoke.java
java -cp "%{buildroot}%{_javadir}/jsoup.jar:." JsoupSmoke jsoup124_ok > check124.log
cat check124.log
grep -F -q 'jsoup124_ok Hello' check124.log
javac --release 8 -encoding UTF-8 -Xlint:-options \
	-cp "%{buildroot}%{_javadir}/jsoup-1.23.2.jar" \
	-d . JsoupSmoke.java
java -cp "%{buildroot}%{_javadir}/jsoup-1.23.2.jar:." JsoupSmoke jsoup123_ok > check123.log
cat check123.log
grep -F -q 'jsoup123_ok Hello' check123.log

%files -f .mfiles
%doc LICENSE README.md
