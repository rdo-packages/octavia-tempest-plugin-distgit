# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%global service octavia
%global plugin octavia-tempest-plugin
%global module octavia_tempest_plugin
%global with_doc 1

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global common_desc \
This package contains Tempest tests to cover the Octavia project. \
Additionally it provides a plugin to automatically load these tests into Tempest.


Name:       python-%{service}-tests-tempest
Version:    XXX
Release:    XXX
Summary:    Tempest Integration of Octavia Project
License:    ASL 2.0
URL:        https://git.openstack.org/cgit/openstack/%{plugin}/

Source0:    http://tarballs.openstack.org/%{plugin}/%{plugin}-%{upstream_version}.tar.gz

BuildRequires:  git
BuildRequires:  openstack-macros

%description
%{common_desc}

%package -n python%{pyver}-%{service}-tests-tempest-golang
Summary:        python%{pyver}-%{service}-tests-tempest golang files
%{?python_provide:%python_provide python%{pyver}-%{service}-tests-tempest-golang}

BuildRequires:  golang
BuildRequires:  glibc-static
%if 0%{?rhel} > 7
BuildRequires:  openssl-static
BuildRequires:  zlib-static
%endif

%description -n python%{pyver}-%{service}-tests-tempest-golang
%{common_desc}

This package contains Octavia tempest golang httpd code.

%package -n python%{pyver}-%{service}-tests-tempest
Summary: %{summary}
BuildArch:  noarch
%{?python_provide:%python_provide python%{pyver}-%{service}-tests-tempest}

BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-setuptools

Obsoletes:      python-octavia-tests < 2.0.0

Requires:       python%{pyver}-%{service}-tests-tempest-golang
Requires:       python%{pyver}-pbr >= 3.1.1
Requires:       python%{pyver}-oslotest >= 3.2.0
Requires:       python%{pyver}-tempest >= 1:18.0.0
Requires:       python%{pyver}-tenacity >= 4.8.0
Requires:       python%{pyver}-dateutil
Requires:       python%{pyver}-octavia-lib >= 1.0.0
Requires:       python%{pyver}-oslo-config
Requires:       python%{pyver}-oslo-log
Requires:       python%{pyver}-oslo-utils
Requires:       python%{pyver}-requests
Requires:       python%{pyver}-six
Requires:       python%{pyver}-cryptography >= 2.1
Requires:       python%{pyver}-barbicanclient >= 4.5.2
Requires:       python%{pyver}-pyOpenSSL >= 17.1.0

# Handle python2 exception
%if %{pyver} == 2
Requires:       python-ipaddress
%endif

%description -n python%{pyver}-%{service}-tests-tempest
%{common_desc}

%if 0%{?with_doc}
%package -n python-%{service}-tests-tempest-doc
Summary:        python-%{service}-tests-tempest documentation

BuildArch:  noarch

BuildRequires:  python%{pyver}-sphinx
BuildRequires:  python%{pyver}-sphinxcontrib-apidoc
BuildRequires:  python%{pyver}-openstackdocstheme
# Required for documentation build
BuildRequires:  python%{pyver}-oslo-config
BuildRequires:  python%{pyver}-tempest

%description -n python-%{service}-tests-tempest-doc
It contains the documentation for the Octavia tempest plugin.
%endif

%prep
%autosetup -n %{plugin}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup
# Remove bundled egg-info
rm -rf %{module}.egg-info

%build
%{pyver_build}

# Generate octavia test httpd binary from httpd.go
pushd %{module}/contrib/httpd
%if 0%{?rhel} > 7
 go build -ldflags '-compressdwarf=false -linkmode external -extldflags "-static -ldl -lz"' -o %{plugin}-tests-httpd httpd.go
%else
 go build -ldflags '-linkmode external -extldflags -static' -o %{plugin}-tests-httpd httpd.go
%endif
popd

# Generate Docs
%if 0%{?with_doc}
export PYTHONPATH=.
sphinx-build-%{pyver} -W -b html doc/source doc/build/html
# remove the sphinx build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%{pyver_install}

# Move httpd binary to proper place
install -d -p %{buildroot}%{_libexecdir}
install -p -m 0755 %{module}/contrib/httpd/%{plugin}-tests-httpd %{buildroot}%{_libexecdir}/%{plugin}-tests-httpd
ln -s -f %{_libexecdir}/%{plugin}-tests-httpd %{buildroot}%{pyver_sitelib}/%{module}/contrib/httpd/httpd.bin

# Remove httpd.go code
rm  %{buildroot}%{pyver_sitelib}/%{module}/contrib/httpd/httpd.go

%files -n python%{pyver}-%{service}-tests-tempest-golang
%{_libexecdir}/%{plugin}-tests-httpd
%{pyver_sitelib}/%{module}/contrib/httpd/httpd.bin

%files -n python%{pyver}-%{service}-tests-tempest
%license LICENSE
%doc README.rst
%exclude %{pyver_sitelib}/%{module}/contrib/httpd/httpd.bin
%{pyver_sitelib}/%{module}
%{pyver_sitelib}/*.egg-info

%if 0%{?with_doc}
%files -n python-%{service}-tests-tempest-doc
%doc doc/build/html
%license LICENSE
%endif

%changelog
# REMOVEME: error caused by commit http://git.openstack.org/cgit/openstack/octavia-tempest-plugin/commit/?id=a2f550348b2b0932f4f452cc7ec53927bc0a073a
