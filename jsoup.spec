Name:		jsoup
Version:	1.19.1
Release:	1
Summary:	Java HTML parser
Group:		Development/Java
License:	MIT
URL:		https://jsoup.org/
Source0:	https://github.com/jhy/jsoup/archive/refs/tags/jsoup-%{version}.tar.gz#/jsoup-%{version}.tar.gz
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	mvn(org.jspecify:jspecify)
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
HTML parser used by Maven plugin tools when they turn Javadoc comments
into descriptor text. The upstream POM turns the default compile off and
passes an Eclipse-only compiler flag, so this build replaces it with a
flat POM. The Java 11 HTTP client overrides are not required to parse HTML.

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
ET.ElementTree(root).write("pom.xml", encoding="utf-8", xml_declaration=True)
PY

%files -f .mfiles
%doc LICENSE README.md
