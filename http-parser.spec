Summary:	HTTP request/response parser for C
Summary(pl.UTF-8):	Analizator żądań/odpowiedzi HTTP dla C
Name:		http-parser
Version:	2.1
Release:	1
License:	MIT
Group:		Libraries
Source0:	https://github.com/joyent/http-parser/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	93d89867996b8077e0140692c55e997c
# Build shared library with SONAME using gyp and remove -O flags so optflags take over
# TODO: do this nicely upstream
Patch0:		%{name}-gyp-sharedlib.patch
URL:		http://github.com/joyent/http-parser
BuildRequires:	libstdc++-devel
BuildRequires:	gyp
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# we use the upstream version from http_parser.h as the SONAME
%define somajor 2
%define sominor 1
%define somicro 0

%description
This is a parser for HTTP messages written in C. It parses both
requests and responses. The parser is designed to be used in
performance HTTP applications. It does not make any syscalls nor
allocations, it does not buffer data, it can be interrupted at
anytime. Depending on your architecture, it only requires about 40
bytes of data per message stream (in a web server that is per
connection).

%description -l pl.UTF-8
Ten pakiet zawiera analizator komunikatów HTTP napisany w C. Analizuje
zarówno żądania, jak i odpowiedzi. Może być używany w zastosowaniach
wymagających dużej wydajności. Nie wykonuje żadnych wywołań
systemowych, nie przydziela pamięci, nie buforuje danych, może być
przerwany w dowolnej chwili. W zależności od architektury wymaga
jedynie około 40 bajtów danych dla strumienia komunikatów (w przypadku
serwera WWW - dla połączenia).

%package devel
Summary:	Development headers for http-parser library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki http-parser
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Development headers for http-parser library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki http-parser.

%prep
%setup -q
%patch0

%build
# TODO: fix -fPIC upstream
export CFLAGS='%{rpmcflags} -fPIC'
gyp -f make --depth=. http_parser.gyp
%{__make} V=1 \
	CC="%{__cc}" \
	CXX="%{__cxx}" \
	BUILDTYPE=Release

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
%attr(755,root,root) %ghost %{_libdir}/libhttp_parser.so.2
%attr(755,root,root) %{_libdir}/libhttp_parser_strict.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libhttp_parser_strict.so.2

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libhttp_parser.so
%attr(755,root,root) %{_libdir}/libhttp_parser_strict.so
%{_includedir}/http_parser.h
