%global service octavia
%global plugin octavia-tempest-plugin
%global module octavia_tempest_plugin
%global with_doc 1

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global common_desc \
This package contains Tempest tests to cover the Octavia project. \
Additionally it provides a plugin to automatically load these tests into Tempest.


Name:       python-%{service}-tests-tempest
Version:    1.7.0
Release:    1%{?dist}
Summary:    Tempest Integration of Octavia Project
License:    ASL 2.0
URL:        https://git.openstack.org/cgit/openstack/%{plugin}/

Source0:    http://tarballs.openstack.org/%{plugin}/%{plugin}-%{upstream_version}.tar.gz

BuildRequires:  git
BuildRequires:  openstack-macros

%description
%{common_desc}

%package -n python3-%{service}-tests-tempest-golang
Summary:        python3-%{service}-tests-tempest golang files
%{?python_provide:%python_provide python3-%{service}-tests-tempest-golang}

BuildRequires:  golang
BuildRequires:  glibc-static
BuildRequires:  openssl-static
BuildRequires:  zlib-static

%description -n python3-%{service}-tests-tempest-golang
%{common_desc}

This package contains Octavia tempest golang httpd code.

%package -n python3-%{service}-tests-tempest
Summary: %{summary}
BuildArch:  noarch
%{?python_provide:%python_provide python3-%{service}-tests-tempest}

BuildRequires:  python3-devel
BuildRequires:  python3-pbr
BuildRequires:  python3-setuptools

Obsoletes:      python-octavia-tests < 2.0.0

Requires:       python3-%{service}-tests-tempest-golang
Requires:       python3-pbr >= 2.0.0
Requires:       python3-oslotest >= 3.2.0
Requires:       python3-tempest >= 1:18.0.0
Requires:       python3-tenacity >= 4.4.0
Requires:       python3-dateutil >= 2.5.3
Requires:       python3-oslo-config >= 5.2.0
Requires:       python3-oslo-log >= 3.36.0
Requires:       python3-oslo-utils >= 3.33.0
Requires:       python3-requests >= 2.14.2
Requires:       python3-six >= 1.10.0
Requires:       python3-cryptography >= 2.1
Requires:       python3-barbicanclient >= 4.5.2
Requires:       python3-pyOpenSSL >= 17.1.0
Requires:       python3-oslo-serialization >= 2.18.0
Requires:       python3-keystoneauth1 >= 3.3.0


%description -n python3-%{service}-tests-tempest
%{common_desc}

%if 0%{?with_doc}
%package -n python-%{service}-tests-tempest-doc
Summary:        python-%{service}-tests-tempest documentation

BuildArch:  noarch

BuildRequires:  python3-sphinx
BuildRequires:  python3-sphinxcontrib-apidoc
BuildRequires:  python3-sphinxcontrib-rsvgconverter
BuildRequires:  python3-openstackdocstheme
# Required for documentation build
BuildRequires:  python3-barbicanclient
BuildRequires:  python3-oslo-config
BuildRequires:  python3-tempest
BuildRequires:  python3-tenacity
BuildRequires:  python3-pyOpenSSL

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
%{py3_build}

rm -f %{module}/contrib/test_server/*bin

# Generate octavia test httpd binary from test_server.go
pushd %{module}/contrib/test_server
%if 0%{?rhel} > 7
 go build -ldflags '-compressdwarf=false -linkmode external -extldflags "-z now -pie -static -ldl -lz"' -o %{plugin}-tests-httpd test_server.go
%else
 go build -ldflags '-linkmode external -extldflags -static' -o %{plugin}-tests-httpd test_server.go
%endif
popd

# Generate Docs
%if 0%{?with_doc}
export PYTHONPATH=.
sphinx-build -b html doc/source doc/build/html
# remove the sphinx build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%{py3_install}

# Move httpd binary to proper place
install -d -p %{buildroot}%{_libexecdir}
install -p -m 0755 %{module}/contrib/test_server/%{plugin}-tests-httpd %{buildroot}%{_libexecdir}/%{plugin}-tests-httpd
ln -s -f %{_libexecdir}/%{plugin}-tests-httpd %{buildroot}%{python3_sitelib}/%{module}/contrib/test_server/test_server.bin

# Remove test_server.go code
rm  %{buildroot}%{python3_sitelib}/%{module}/contrib/test_server/test_server.go

%files -n python3-%{service}-tests-tempest-golang
%{_libexecdir}/%{plugin}-tests-httpd
%{python3_sitelib}/%{module}/contrib/test_server/test_server.bin

%files -n python3-%{service}-tests-tempest
%license LICENSE
%doc README.rst
%exclude %{python3_sitelib}/%{module}/contrib/test_server/test_server.bin
%{python3_sitelib}/%{module}
%{python3_sitelib}/*.egg-info

%if 0%{?with_doc}
%files -n python-%{service}-tests-tempest-doc
%doc doc/build/html
%license LICENSE
%endif

%changelog
* Fri Apr 09 2021 RDO <dev@lists.rdoproject.org> 1.7.0-1
- Update to 1.7.0

