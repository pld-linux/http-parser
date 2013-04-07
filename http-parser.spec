%define git_date 20121128
%define git_commit_hash cd01361
%define github_seq 7
Summary:	HTTP request/response parser for C
Name:		http-parser
Version:	2.0
Release:	0.git%{git_commit_hash}
License:	MIT
Group:		Libraries
URL:		http://github.com/joyent/http-parser
# download from https://github.com/joyent/http-parser/tarball/%%{version}
Source0:	http://pkgs.fedoraproject.org/repo/pkgs/http-parser/joyent-%{name}-v%{version}-%{github_seq}-g%{git_commit_hash}.tar.gz/340f2aab333c435cbaf49a4949645a06/joyent-http-parser-v%{version}-%{github_seq}-g%{git_commit_hash}.tar.gz
# Source0-md5:	340f2aab333c435cbaf49a4949645a06
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
# Build shared library with SONAME using gyp and remove -O flags so optflags take over
# TODO: do this nicely upstream
Patch1:		%{name}-gyp-sharedlib.patch
BuildRequires:	gyp
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# we use the upstream version from http_parser.h as the SONAME
%define somajor 2
%define sominor 0
%define somicro 0

%description
This is a parser for HTTP messages written in C. It parses both
requests and responses. The parser is designed to be used in
performance HTTP applications. It does not make any syscalls nor
allocations, it does not buffer data, it can be interrupted at
anytime. Depending on your architecture, it only requires about 40
bytes of data per message stream (in a web server that is per
connection).

%package devel
Summary:	Development headers and libraries for http-parser
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Development headers and libraries for http-parser.

%prep
%setup -q -n joyent-%{name}-%{git_commit_hash}
%patch1

%build
# TODO: fix -fPIC upstream
export CFLAGS='%{optflags} -fPIC'
gyp -f make --depth=. http_parser.gyp
%{__make} V=1 BUILDTYPE=Release

%if %{with tests}
export LD_LIBRARY_PATH='./out/Release/lib.target'
./out/Release/test-nonstrict
./out/Release/test-strict
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir},%{_includedir}}
cp -p http_parser.h $RPM_BUILD_ROOT%{_includedir}

# install regular variant
install -p out/Release/lib.target/libhttp_parser.so.%{somajor} $RPM_BUILD_ROOT%{_libdir}/libhttp_parser.so.%{somajor}.%{sominor}.%{somicro}
lib=$(basename $RPM_BUILD_ROOT%{_libdir}/libhttp_parser.so.*.*.*)
ln -s $lib $RPM_BUILD_ROOT%{_libdir}/libhttp_parser.so.%{somajor}
ln -s $lib $RPM_BUILD_ROOT%{_libdir}/libhttp_parser.so

# install strict variant
install -p out/Release/lib.target/libhttp_parser_strict.so.%{somajor} $RPM_BUILD_ROOT%{_libdir}/libhttp_parser_strict.so.%{somajor}.%{sominor}.%{somicro}
lib=$(basename $RPM_BUILD_ROOT%{_libdir}/libhttp_parser_strict.so.*.*.*)
ln -s $lib $RPM_BUILD_ROOT%{_libdir}/libhttp_parser_strict.so.%{somajor}
ln -s $lib $RPM_BUILD_ROOT%{_libdir}/libhttp_parser_strict.so

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS CONTRIBUTIONS LICENSE-MIT README.md
%attr(755,root,root) %{_libdir}/libhttp_parser.so.*.*.*
%ghost %{_libdir}/libhttp_parser.so.2
%attr(755,root,root) %{_libdir}/libhttp_parser_strict.so.*.*.*
%ghost %{_libdir}/libhttp_parser_strict.so.2

%files devel
%defattr(644,root,root,755)
%{_includedir}/http_parser.h
%{_libdir}/libhttp_parser.so
%{_libdir}/libhttp_parser_strict.so
