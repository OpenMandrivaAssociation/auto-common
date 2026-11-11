Name:		auto-common
Version:	1.2.2
Release:	1
Summary:	Utilities for writing annotation processors
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/google/auto
Source0:	https://github.com/google/auto/archive/refs/tags/auto-common-%{version}.tar.gz#/auto-common-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	mvn(com.google.guava:guava)
BuildRequires:	mvn(com.squareup:javapoet)
BuildRequires:	mvn(org.checkerframework:checker-qual)

%description
Auto Common %{version} is the shared utility library used by AutoValue
and other annotation processors. This is the 1.2.2 tag, which annotates
its API with Checker Framework @Nullable.

%prep
%autosetup -n auto-auto-common-%{version} -p1
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
find common/src/main/java -name '*.java' ! -name 'module-info.java' > sources.list
test "$(wc -l < sources.list)" -eq 15
mkdir -p classes
javac --release 11 -encoding UTF-8 \
	-cp %{_javadir}/guava.jar:%{_javadir}/failureaccess.jar:%{_javadir}/javapoet.jar:%{_javadir}/checker-qual.jar \
	-d classes @sources.list
jar cf auto-common.jar -C classes .
jar tf auto-common.jar | grep -E '\.(java|jar|so|node|wasm)$' && exit 1 || true
javap -verbose -cp auto-common.jar com.google.auto.common.MoreStreams | grep -F 'major version: 55'

cat > auto-common.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.google.auto</groupId>
  <artifactId>auto-common</artifactId>
  <version>1.2.2</version>
  <name>Auto Common</name>
  <description>Utilities for writing annotation processors</description>
  <licenses>
    <license>
      <name>Apache-2.0</name>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>com.google.guava</groupId>
      <artifactId>guava</artifactId>
      <version>33.6.0-jre</version>
    </dependency>
    <dependency>
      <groupId>org.checkerframework</groupId>
      <artifactId>checker-qual</artifactId>
      <version>4.4.0</version>
    </dependency>
    <dependency>
      <groupId>com.squareup</groupId>
      <artifactId>javapoet</artifactId>
      <version>1.13.0</version>
      <optional>true</optional>
    </dependency>
  </dependencies>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact auto-common.pom:auto-common.jar \
	--file-name auto-common \
	--filelist .mfiles

%check
mkdir -p check
cat > check/Smoke.java << 'END'
import com.google.auto.common.MoreStreams;
import com.google.common.collect.ImmutableList;
import java.util.stream.Stream;
public class Smoke {
	public static void main(String[] args) {
		ImmutableList<String> list = Stream.of("auto", "common").collect(MoreStreams.toImmutableList());
		if (list.size() != 2 || !"auto".equals(list.get(0)) || !"common".equals(list.get(1))) {
			throw new RuntimeException("bad list " + list);
		}
		System.out.println("auto_common_ok " + list.get(0) + " " + list.get(1));
	}
}
END
JAR=%{buildroot}%{_javadir}/auto-common.jar
test -f "$JAR"
CP="$JAR:%{_javadir}/guava.jar:%{_javadir}/failureaccess.jar:%{_javadir}/checker-qual.jar"
javac --release 11 -encoding UTF-8 -cp "$CP" -d check check/Smoke.java
java -cp "check:$CP" Smoke > check/out.txt
cat check/out.txt
grep -F -q 'auto_common_ok auto common' check/out.txt

%files -f .mfiles
%doc LICENSE
