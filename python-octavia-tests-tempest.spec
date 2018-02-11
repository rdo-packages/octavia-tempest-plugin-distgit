%global service octavia
%global plugin octavia-tempest-plugin
%global module octavia_tempest_plugin
%global with_doc 1

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%if 0%{?fedora}
%global with_python3 1
%endif

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

%package -n python-%{service}-tests-tempest-golang
Summary:        python2-%{service}-tests-tempest golang files

BuildRequires:  golang
BuildRequires:  glibc-static

%description -n python-%{service}-tests-tempest-golang
%{common_desc}

This package contains Octavia tempest golang httpd code.

%package -n python2-%{service}-tests-tempest
Summary: %{summary}
BuildArch:  noarch
%{?python_provide:%python_provide python2-%{service}-tests-tempest}
BuildRequires:  python2-devel
BuildRequires:  python2-pbr
BuildRequires:  python2-setuptools

Requires:       python-%{service}-tests-tempest-golang = %{version}-%{release}
Requires:       python2-pbr >= 2.0
Requires:       python2-oslotest >= 1.10.0
Requires:       python2-tempest >= 1:17.2.0
Requires:       python2-tenacity >= 3.2.1

%description -n python2-%{service}-tests-tempest
%{common_desc}

%if 0%{?with_doc}
%package -n python-%{service}-tests-tempest-doc
Summary:        python-%{service}-tests-tempest documentation

BuildArch:  noarch

BuildRequires:  python2-sphinx
BuildRequires:  python2-oslo-sphinx
BuildRequires:  python2-openstackdocstheme

%description -n python-%{service}-tests-tempest-doc
It contains the documentation for the Octavia tempest plugin.
%endif

%if 0%{?with_python3}
%package -n python3-%{service}-tests-tempest
Summary: %{summary}
BuildArch:  noarch
%{?python_provide:%python_provide python3-%{service}-tests-tempest}


BuildRequires:  python3-devel
BuildRequires:  python3-pbr
BuildRequires:  python3-setuptools

Requires:       python-%{service}-tests-tempest-golang = %{version}-%{release}
Requires:       python3-pbr >= 2.0
Requires:       python3-oslotest >= 1.10.0
Requires:       python3-tempest >= 1:17.2.0
Requires:       python3-tenacity >= 3.2.1

%description -n python3-%{service}-tests-tempest
%{common_desc}
%endif

%prep
%autosetup -n %{plugin}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup
# Remove bundled egg-info
rm -rf %{module}.egg-info

%build
%if 0%{?with_python3}
%py3_build
%endif
%py2_build

# Generate octavia test httpd binary from httpd.go
pushd %{module}/contrib/httpd
 go build -ldflags '-linkmode external -extldflags -static' -o %{plugin}-tests-httpd httpd.go
popd

# Generate Docs
%if 0%{?with_doc}
%{__python2} setup.py build_sphinx -b html
# remove the sphinx build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%if 0%{?with_python3}
%py3_install
%endif
%py2_install

# Move httpd binary to proper place
install -d -p %{buildroot}%{_bindir}
install -p -m 0755 %{module}/contrib/httpd/%{plugin}-tests-httpd %{buildroot}%{_bindir}

# Replace the path with its binary
sed -e "/^SERVER_BINARY =/{N;s#pkg_resources.*#'/usr/bin/%{plugin}-tests-httpd'#}" \
    -i %{buildroot}%{python2_sitelib}/%{module}/tests/server_util.py

# Remove httpd.go code
rm  %{buildroot}%{python2_sitelib}/%{module}/contrib/httpd/httpd.{bin,go}

# And for python3
%if 0%{?with_python3}
sed -e "/^SERVER_BINARY =/{N;s#pkg_resources.*#'/usr/bin/%{plugin}-tests-httpd'#}" \
    -i %{buildroot}%{python3_sitelib}/%{module}/tests/server_util.py
rm  %{buildroot}%{python3_sitelib}/%{module}/contrib/httpd/httpd.{bin,go}
%endif

%files -n python-%{service}-tests-tempest-golang
%{_bindir}/%{plugin}-tests-httpd

%files -n python2-%{service}-tests-tempest
%license LICENSE
%doc README.rst
%{python2_sitelib}/%{module}
%{python2_sitelib}/*.egg-info

%if 0%{?with_python3}
%files -n python3-%{service}-tests-tempest
%license LICENSE
%doc README.rst
%{python3_sitelib}/%{module}
%{python3_sitelib}/*.egg-info
%endif

%if 0%{?with_doc}
%files -n python-%{service}-tests-tempest-doc
%doc doc/build/html
%license LICENSE
%endif

%changelog
