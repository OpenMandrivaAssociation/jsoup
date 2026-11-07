Name:		jsoup
Version:	1.24.1
Release:	1
Summary:	Java HTML parser
Group:		Development/Java
License:	MIT
URL:		https://jsoup.org/
Source0:	https://github.com/jhy/jsoup/archive/refs/tags/jsoup-%{version}.tar.gz#/jsoup-%{version}.tar.gz

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
org.jsoup.

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

%build -a
cat > manifest-addition <<'EOF'
Automatic-Module-Name: org.jsoup
EOF
jar ufm target/jsoup-%{version}.jar manifest-addition
java --module-path target/jsoup-%{version}.jar --describe-module org.jsoup | grep -q '^org.jsoup'

%files -f .mfiles
%doc LICENSE README.md
