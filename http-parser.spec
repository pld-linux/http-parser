#
# Conditional build:
%bcond_without	tests		# unit tests
#
Summary:	HTTP request/response parser for C
Summary(pl.UTF-8):	Analizator żądań/odpowiedzi HTTP dla C
Name:		http-parser
Version:	2.9.4
Release:	3
License:	MIT
Group:		Libraries
#Source0Download: https://github.com/nodejs/http-parser/releases
# upstream archived in 2020, 2.9.4 is the final release
Source0:	https://github.com/nodejs/http-parser/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	1b0f2371aabacbadaa03cc532cedcf92
Patch0:		%{name}-sizeof-assert.patch
URL:		https://github.com/nodejs/http-parser
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# version taken from http_parser.h; SONAME is .so.%{somajor}, not upstream Makefile's .so.%{somajor}.%{sominor}
%define		somajor	2
%define		sominor	9
%define		somicro	4

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
%patch -P0 -p1

%build
export CPPFLAGS="%{rpmcppflags}"
export LDFLAGS="%{rpmldflags}"
# upstream hardcodes -O3/-O0 into its own CFLAGS_* variables, override them so optflags take over
cflags="%{rpmcflags} -Wall -Wextra -Werror"

# regular variant
%{__make} library \
	CC="%{__cc}" \
	CFLAGS_FAST="$cflags" \
	SONAME=libhttp_parser.so.%{somajor} \
	LIBNAME=libhttp_parser.so.%{somajor}.%{sominor}.%{somicro}

# upstream hardcodes the object file name, the strict build would reuse the regular object
rm libhttp_parser.o

# strict variant
%{__make} library \
	CC="%{__cc}" \
	CFLAGS_FAST="$cflags" \
	CPPFLAGS_FAST="$CPPFLAGS -I. -DHTTP_PARSER_STRICT=1" \
	SONAME=libhttp_parser_strict.so.%{somajor} \
	LIBNAME=libhttp_parser_strict.so.%{somajor}.%{sominor}.%{somicro}

%if %{with tests}
%{__make} test \
	CC="%{__cc}" \
	CFLAGS_FAST="$cflags" \
	CFLAGS_DEBUG="$cflags -g"
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir},%{_includedir}}
cp -p http_parser.h $RPM_BUILD_ROOT%{_includedir}

# install regular variant
install -p libhttp_parser.so.%{somajor}.%{sominor}.%{somicro} $RPM_BUILD_ROOT%{_libdir}
ln -s libhttp_parser.so.%{somajor}.%{sominor}.%{somicro} $RPM_BUILD_ROOT%{_libdir}/libhttp_parser.so.%{somajor}
ln -s libhttp_parser.so.%{somajor}.%{sominor}.%{somicro} $RPM_BUILD_ROOT%{_libdir}/libhttp_parser.so

# install strict variant
install -p libhttp_parser_strict.so.%{somajor}.%{sominor}.%{somicro} $RPM_BUILD_ROOT%{_libdir}
ln -s libhttp_parser_strict.so.%{somajor}.%{sominor}.%{somicro} $RPM_BUILD_ROOT%{_libdir}/libhttp_parser_strict.so.%{somajor}
ln -s libhttp_parser_strict.so.%{somajor}.%{sominor}.%{somicro} $RPM_BUILD_ROOT%{_libdir}/libhttp_parser_strict.so

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS LICENSE-MIT README.md
%attr(755,root,root) %{_libdir}/libhttp_parser.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libhttp_parser.so.2
%attr(755,root,root) %{_libdir}/libhttp_parser_strict.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libhttp_parser_strict.so.2

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libhttp_parser.so
%attr(755,root,root) %{_libdir}/libhttp_parser_strict.so
%{_includedir}/http_parser.h
