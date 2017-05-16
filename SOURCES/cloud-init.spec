%define _buildid .15

%global python_sitelib %{sys_python_sitelib}
%global __python %{__sys_python}

%bcond_with systemd
%bcond_with selinux
# The Amazon Linux AMI build of cloud-init does not log using syslog by default
# because we found that rate-limiting caused some loss of log data.
%bcond_with rsyslog # without

# dmidecode is only used for a handful of alternative cloud providers
%bcond_with dmidecode # without
%if %{with dmidecode}
# The only reason we are archful is because dmidecode is ExclusiveArch
# https://bugzilla.redhat.com/show_bug.cgi?id=1067089
%global debug_package %{nil}
%endif

Name:           cloud-init
Version:        0.7.6
Release: 2%{?_buildid}%{?dist}
Summary:        Cloud instance init scripts

Group:          System Environment/Base
License:        GPLv3
URL:            http://launchpad.net/cloud-init
Source0:        https://launchpad.net/cloud-init/trunk/%{version}/+download/%{name}-%{version}.tar.gz
Source1:        cloud-init-amazon.cfg
Source2:        cloud-init-README.fedora
Source3:        cloud-init-tmpfiles.conf

# Deal with Fedora/Ubuntu path differences
Patch0:         Move-helper-tools-to-usr-lib.patch

# Fix rsyslog log filtering
# https://code.launchpad.net/~gholms/cloud-init/rsyslog-programname/+merge/186906
Patch1:         cloud-init-0.7.5-rsyslog-programname.patch

# Systemd 213 removed the --quiet option from ``udevadm settle''
Patch2:         cloud-init-0.7.5-udevadm-quiet.patch

%if %{with dmidecode}
# Deal with noarch -> arch
# https://bugzilla.redhat.com/show_bug.cgi?id=1067089
Obsoletes:      cloud-init < 0.7.5-3
%endif

# Amazon sources and patches
Source10:       defaults-amazon.cfg

Patch10001:     0001-Add-an-Amazon-distro-module.patch
Patch10002:     0002-Correct-usage-of-os.uname.patch
Patch10003:     0003-Decode-userdata-if-it-is-base64-encoded.patch
Patch10004:     0004-Add-pipe_cat-and-close_stdin-options-for-subp.patch
Patch10005:     0005-repo_upgrade-handling-security-levels.patch
Patch10006:     0006-Add-amazon-to-redhat-OS-family.patch
Patch10007:     0007-Amazon-Linux-AMI-doesn-t-use-systemd.patch
Patch10008:     0008-Add-a-genrepo-module-to-populate-yum.repos.d.patch
Patch10009:     0009-Use-a-shell-for-user-supplied-scripts.patch
Patch10010:     0010-Better-logging-for-the-power-state-change-module.patch
Patch10011:     0011-Add-repo_additions-compatibility.patch
Patch10012:     0012-Use-instance-identity-doc-for-region-and-instance-id.patch
Patch10013:     0013-Expand-the-migrator-module-to-handle-more-legacy.patch
Patch10014:     0014-Improve-service-handling.patch
Patch10015:     0015-Don-t-use-cheetah-for-formatting-log-entries.patch
Patch10016:     0016-Have-rsyslog-filter-on-syslogtag-startswith-CLOUDINI.patch
Patch10017:     0017-Suppress-backports-UserWarning-in-url_helper.patch
Patch10018:     0018-Catch-UrlError-when-includeing-URLs.patch
Patch10019:     0019-Prefer-file-to-syslog-and-improve-format.patch
Patch10020:     0020-Determine-services-domain-dynamically.patch
Patch10021:     0021-Remove-prettytable-dependency.patch
Patch10022:     0022-Use-legacy-sudoers-file.patch
Patch10023:     0023-Add-chkconfig-directives-move-cloud-final-near-end.patch
Patch10024:     0024-Create-write-metadata-module.patch
Patch10025:     0025-Print-permissions-as-octal-not-decimal.patch
Patch10026:     0026-Repair-mounts-module.patch
Patch10027:     0027-lock-passwd-SELinux-compatibility.patch
Patch10028:     0028-Suppress-Cheetah-not-available-warning.patch
Patch10029:     0029-Enable-resolv-conf-module.patch
Patch10030:     0030-Produce-canonical-semaphore-names-with-cloud-init-per.patch
Patch10031:     0031-Remove-call-to-yum-makecache-in-distros.rhel.patch
Patch10032:     0032-Don-t-cache-security-credentials-on-disk.patch

# Upstream patches
# https://launchpad.net/bugs/1387340
# 'output' directive not honored (/var/log/cloud-init-output.log missing)
Patch20001:     lp1387340-bzr1030.patch
# https://launchpad.net/bugs/1246485
# non-persistent hostname is the 'short' hostname
Patch20002:     lp1246485-bzr1052.patch
# https://launchpad.net/bugs/1465436
# growpart does not respect devices list
Patch20003:     lp1465436-git6e06aff.patch

%if %{without dmidecode}
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  system-python-devel
BuildRequires:  %{sys_python_pkg}-setuptools
BuildRequires:  git
%if %{with systemd}
BuildRequires:  systemd-units
%endif
%if %{with dmidecode}
%ifarch %{?ix86} x86_64 ia64
Requires:       dmidecode
%endif
%endif
Requires:       e2fsprogs
Requires:       iproute
%if %{with selinux}
Requires:       libselinux-python(%sys_python_pkg)
%endif
Requires:       net-tools
Requires:       procps
#Requires:       python-argparse
Requires:       %{sys_python_pkg}-configobj
Requires:       %{sys_python_pkg}-jinja2
Requires:       %{sys_python_pkg}-requests
Requires:       %{sys_python_pkg}-PyYAML
%if %{with rsyslog}
Requires:       rsyslog
%endif
Requires:       %{sys_python_pkg}-jsonpatch
Requires:       shadow-utils
%if %{with systemd}
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%else
Requires(post):   chkconfig
Requires(preun):  chkconfig
Requires(postun): initscripts
# For triggerun hacks for 0.5+
Requires: upstart
Requires: /sbin/initctl
Requires: /sbin/service
Requires: mktemp
Requires: /usr/bin/rename
%endif

Provides:       cloud-init(genrepo)

%description
Cloud-init is a set of init scripts for cloud instances.  Cloud instances
need special scripts to run during initialization to retrieve and install
ssh keys and to let the user run various scripts.


%prep
%autosetup -Sgit -n %{name}-%{version}

cp -p %{SOURCE2} README.fedora


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT \
%if %{with systemd}
    --init-system=systemd
%else
    --init-system=sysvinit
%endif


# setup.py copies everything in config/cloud.cfg.d, including patch backups
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/cloud/cloud.cfg.d/*.orig

# Remove other cloud sources
for source in \
    $(ls $RPM_BUILD_ROOT%{python_sitelib}/cloudinit/sources/DataSource* \
      | grep -iv 'DataSourceEc2\|DataSourceNone')
do
    rm -f $source
done
rm -f $RPM_BUILD_ROOT%{python_sitelib}/cloudinit/sources/helpers/openstack*
# The rightscale user-data source is incorrectly implemented as a module...
rm -f $RPM_BUILD_ROOT%{python_sitelib}/cloudinit/config/cc_rightscale*

# Don't ship the tests
rm -r $RPM_BUILD_ROOT%{python_sitelib}/tests

mkdir -p $RPM_BUILD_ROOT/%{_sharedstatedir}/cloud

# We supply our own config file since our software differs from Ubuntu's.
cp -p %{SOURCE1} $RPM_BUILD_ROOT/%{_sysconfdir}/cloud/cloud.cfg
cp -p %{SOURCE10} $RPM_BUILD_ROOT/%{_sysconfdir}/cloud/cloud.cfg.d/00_defaults.cfg

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/rsyslog.d
cp -p tools/21-cloudinit.conf $RPM_BUILD_ROOT/%{_sysconfdir}/rsyslog.d/21-cloudinit.conf

%if %{with systemd}
# /run/cloud-init needs a tmpfiles.d entry
mkdir -p $RPM_BUILD_ROOT/run/cloud-init
mkdir -p         $RPM_BUILD_ROOT/%{_tmpfilesdir}
cp -p %{SOURCE3} $RPM_BUILD_ROOT/%{_tmpfilesdir}/%{name}.conf
%endif

# Add sudo entry for ec2-user in /etc/sudoers.d
# cloud-init will do this itself, but if we don't keep this file, an upgrade
# from 0.5 would remove sudo permissions from the ec2-user
install -m 750 -d $RPM_BUILD_ROOT%{_sysconfdir}/sudoers.d
echo "ec2-user ALL = NOPASSWD: ALL" > %{buildroot}%{_sysconfdir}/sudoers.d/cloud-init

# Create a compatibility wrapper for cloud-init-cfg
cat <<'EOF' > $RPM_BUILD_ROOT/%{_bindir}/cloud-init-cfg
#!/bin/sh
%{_bindir}/cloud-init single --name "$@"
EOF
chmod +x $RPM_BUILD_ROOT/%{_bindir}/cloud-init-cfg

%clean
rm -rf $RPM_BUILD_ROOT


%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    # Enabled by default per "runs once then goes away" exception
%if %{with systemd}
    /bin/systemctl enable cloud-config.service     >/dev/null 2>&1 || :
    /bin/systemctl enable cloud-final.service      >/dev/null 2>&1 || :
    /bin/systemctl enable cloud-init.service       >/dev/null 2>&1 || :
    /bin/systemctl enable cloud-init-local.service >/dev/null 2>&1 || :
%else
    for svc in init-local init config final; do
        chkconfig --add cloud-$svc ||:
        chkconfig cloud-$svc on ||:
    done
%endif
fi

%triggerun -- cloud-init < 0.7
# Older versions had different service script names and start priorities
for svc in init init-user-scripts; do
    chkconfig --del cloud-$svc ||:
done

%triggerpostun -- cloud-init < 0.7
for svc in init-local init config final; do
    chkconfig --add cloud-$svc ||:
    chkconfig cloud-$svc on ||:
done
# If cloud-init has already run, we should try to migrate semaphores
if [ -f %{_sharedstatedir}/cloud/data/cache/obj.pkl ]
then
    tmpfile=$(mktemp)
    # Only run the migrator module, nothing else
    echo 'cloud_init_modules: [ migrator ]' > ${tmpfile}
    %{_bindir}/cloud-init --file ${tmpfile} init >/dev/null 2>&1 ||:
    rm -f ${tmpfile}
fi
%if %{without systemd}
# Only create this job if rc is running, so that we are likely to get a started
# event from cloud-init.
if /sbin/initctl status rc | grep start/running >/dev/null 2>&1
then
    UPGRADE_JOB="%{_sysconfdir}/init/cloud-init-upgraded.conf"
    cat <<EOF > "$UPGRADE_JOB"
start on started cloud-init
task
# This file should only exist just after an upgrade from cloud-init 0.5,
# and only if cloud-init was running at the time. We do this to ensure that
# cloud-init completes a run if it happens to upgrade itself.
script
    /sbin/service cloud-init-local start ||:
    /sbin/service cloud-init start ||:
    /sbin/service cloud-config start ||:
    /sbin/service cloud-final start ||:
end script
pre-start exec rm -f "$UPGRADE_JOB"
EOF
fi
%endif

%triggerpostun -- cloud-init < 0.7.2-7.21
# Order matters if you have two triggerpostuns that could apply to a particular
# package being removed -- only the first one that applies is run. This trigger
# comes after the < 0.7 trigger so that it will only run if the version being
# removed is >= 0.7, but < 0.7.2-7.21.

%if %{without systemd}
# The start priority of the cloud-final phase was changed after 0.7.2-7.20
chkconfig cloud-final resetpriorities ||:

# If the start priority change comes while rc is running, we need a hack to get
# cloud-final running.
if /sbin/initctl status rc | grep start/running >/dev/null 2>&1
then
    UPGRADE_JOB="%{_sysconfdir}/init/cloud-final-reprioritized.conf"
    cat <<EOF > "$UPGRADE_JOB"
start on started cloud-config
task
# This file should only exist just after an upgrade from cloud-init >= 0.7,
# but < 0.7.2-7.21, and only if cloud-init was running at the time. This
# ensures that cloud-final gets run if cloud-init upgrades itself.
script
    /sbin/service cloud-final start ||:
end script
pre-start exec rm -f "$UPGRADE_JOB"
EOF
fi
%endif
# 0.7.6 dropped the requirement on Boto, but the old pickle file
# may contain references to it, so delete on upgrade.
if [ -h %{_sharedstatedir}/cloud/instance ] \
  && [ -e %{_sharedstatedir}/cloud/instance/obj.pkl ] ; then
    mv %{_sharedstatedir}/cloud/instance/obj.pkl{,.rpmsave} ||:
else
    rename obj.pkl obj.pkl.rpmsave %{_sharedstatedir}/cloud/instances/*/obj.pkl 2>/dev/null ||:
fi
# In 0.7.5, the consume-userdata semaphore changed to consume-data
# We added that transition to the migrator module in 0.7.6.
# Run the full `cloud-init init` phase to ensure it has the instance ID,
# and run the new write_metadata module now rather than on reboot.
# (This recreates the cached pickle file.)
tmpfile=$(mktemp)
echo 'cloud_init_modules: [ migrator, write-metadata ]' > ${tmpfile}
%{_bindir}/cloud-init --file ${tmpfile} init >/dev/null 2>&1 ||:
rm -f ${tmpfile}


%triggerpostun -- cloud-init < 0.7.6
# 0.7.6 dropped the requirement on Boto, but the old pickle file
# may contain references to it, so delete on upgrade.
if [ -h %{_sharedstatedir}/cloud/instance ] \
  && [ -e %{_sharedstatedir}/cloud/instance/obj.pkl ] ; then
    mv %{_sharedstatedir}/cloud/instance/obj.pkl{,.rpmsave} ||:
else
    rename obj.pkl obj.pkl.rpmsave %{_sharedstatedir}/cloud/instances/*/obj.pkl 2>/dev/null ||:
fi
# In 0.7.5, the consume-userdata semaphore changed to consume-data
# We added that transition to the migrator module in 0.7.6.
# Run the full `cloud-init init` phase to ensure it has the instance ID,
# and run the new write_metadata module now rather than on reboot.
# (This recreates the cached pickle file.)
tmpfile=$(mktemp)
echo 'cloud_init_modules: [ migrator, write-metadata ]' > ${tmpfile}
%{_bindir}/cloud-init --file ${tmpfile} init >/dev/null 2>&1 ||:
rm -f ${tmpfile}

%triggerpostun -- system-release < 2014.09
# We moved to repository files being static, not templates, in system-release
# 2014.09, which use yum vars to fill in the AWS region and domain in the URLs.
# Manually run the write-metadata module to properly fill in the yum vars
# instead of leaving the defaults after an upgrade.
%{_bindir}/cloud-init single --name write-metadata >/dev/null 2>&1 ||:

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
%if %{with systemd}
    /bin/systemctl --no-reload disable cloud-config.service >/dev/null 2>&1 || :
    /bin/systemctl --no-reload disable cloud-final.service  >/dev/null 2>&1 || :
    /bin/systemctl --no-reload disable cloud-init.service   >/dev/null 2>&1 || :
    /bin/systemctl --no-reload disable cloud-init-local.service >/dev/null 2>&1 || :
%else
    for svc in init-local init config final; do
        chkconfig --del cloud-$svc
    done
    # One-shot services -> no need to stop
%endif
fi

%if %{with systemd}
%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
# One-shot services -> no need to restart
%endif


%files
%{!?_licensedir: %global license %%doc}
%license LICENSE
%doc ChangeLog README.fedora
# This file is noreplace because in previous versions it was the only config
# and is more likely to contain customer modifications.
%config(noreplace) %{_sysconfdir}/cloud/cloud.cfg
%dir               %{_sysconfdir}/cloud/cloud.cfg.d
# The defaults config file is new in 0.7 and has comments warning users not to
# modify its contents, and that it will be replaced on upgrade.
%config            %{_sysconfdir}/cloud/cloud.cfg.d/00_defaults.cfg
%config(noreplace) %{_sysconfdir}/cloud/cloud.cfg.d/05_logging.cfg
%doc               %{_sysconfdir}/cloud/cloud.cfg.d/README
%dir               %{_sysconfdir}/cloud/templates
%config(noreplace) %{_sysconfdir}/cloud/templates/*.tmpl
%if %{with systemd}
%{_unitdir}/cloud-config.service
%{_unitdir}/cloud-config.target
%{_unitdir}/cloud-final.service
%{_unitdir}/cloud-init-local.service
%{_unitdir}/cloud-init.service
%{_tmpfilesdir}/%{name}.conf
%dir /run/cloud-init
%else
%{_initddir}/cloud-config
%{_initddir}/cloud-final
%{_initddir}/cloud-init
%{_initddir}/cloud-init-local
%endif
%{python_sitelib}/*.egg-info
%dir %{python_sitelib}/cloudinit
%{python_sitelib}/cloudinit/*.py*
%dir %{python_sitelib}/cloudinit/config
%{python_sitelib}/cloudinit/config/*.py*
%dir %{python_sitelib}/cloudinit/distros
%{python_sitelib}/cloudinit/distros/*.py*
%dir %{python_sitelib}/cloudinit/distros/parsers
%{python_sitelib}/cloudinit/distros/parsers/*.py*
%dir %{python_sitelib}/cloudinit/filters
%{python_sitelib}/cloudinit/filters/*.py*
%dir %{python_sitelib}/cloudinit/handlers
%{python_sitelib}/cloudinit/handlers/*.py*
%dir %{python_sitelib}/cloudinit/mergers
%{python_sitelib}/cloudinit/mergers/*.py*
%dir %{python_sitelib}/cloudinit/sources
%{python_sitelib}/cloudinit/sources/__init__.py*
%{python_sitelib}/cloudinit/sources/DataSourceEc2.py*
%{python_sitelib}/cloudinit/sources/DataSourceNone.py*
%dir %{python_sitelib}/cloudinit/sources/helpers
%{python_sitelib}/cloudinit/sources/helpers/*.py*
%{_libexecdir}/%{name}
%{_bindir}/cloud-init*
%doc %{_datadir}/doc/%{name}
%dir %{_sharedstatedir}/cloud

%dir %{_sysconfdir}/rsyslog.d
%config(noreplace) %{_sysconfdir}/rsyslog.d/21-cloudinit.conf

%config %attr(0440,root,root) %{_sysconfdir}/sudoers.d/cloud-init

%changelog
* Fri Mar 24 2017 Iliana Weller <iweller@amazon.com>
- Fix specification of devices list in growpart (LP #1465436)

* Mon Nov 14 2016 Andrew Jorgensen <ajorgens@amazon.com>
- Migrator should not copy user scripts from 0.5

* Thu Oct 27 2016 Andrew Jorgensen <ajorgens@amazon.com>
- Don't cache security credentials on disk

* Thu Aug 18 2016 Ian Weller <iweller@amazon.com>
- Remove call to "yum makecache" in distros.rhel

* Thu Jan 14 2016 Sean Kelly <seankell@amazon.com>
- Produce canonical semaphore names with cloud-init-per

* Fri Sep 4 2015 Andrew Jorgensen <ajorgens@amazon.com>
- Enable resolv-conf module

* Thu Sep 3 2015 Andrew Jorgensen <ajorgens@amazon.com>
- Add chkconfig directives to workaround bug in ntsysv

* Fri Aug 14 2015 Andrew Jorgensen <ajorgens@amazon.com>
- Suppress Cheetah not available warning
- lock-passwd SELinux compatibility
- Fix service control arguments accumulating

* Tue Mar 24 2015 Ben Cressey <bcressey@amazon.com>
- Remove pickled data and re-run init on upgrade

* Tue Feb 24 2015 Andrew Jorgensen <ajorgens@amazon.com>
- Resolve intervening symlinks

* Thu Feb 5 2015 Ben Cressey <bcressey@amazon.com>
- build with system python

* Tue Dec 2 2014 Andrew Jorgensen <ajorgens@amazon.com>
- import source package F22/cloud-init-0.7.6-2.fc22
- import source package F22/cloud-init-0.7.5-8.fc22
- import source package F21/cloud-init-0.7.5-6.fc21
- import source package F21/cloud-init-0.7.5-5.fc21
- import source package F20/cloud-init-0.7.2-10.fc20
- import source package F20/cloud-init-0.7.2-9.fc20

* Fri Nov 14 2014 Colin Walters <walters@redhat.com> - 0.7.6-1
- New upstream version [RH:974327]
- Drop python-cheetah dependency (same as above bug)

* Fri Nov  7 2014 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.5-8
- Dropped python-boto dependency [RH:1161257]
- Dropped rsyslog dependency [RH:986511]

* Thu Sep 11 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Add upstream patch: provide default 'output' setting to log

* Wed Sep 10 2014 Ben Cressey <bcressey@amazon.com>
- add patch for chef omnibus installation support
- use distro preference for non-persistent hostname

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.5-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Aug 8 2014 Ian Weller <iweller@amazon.com>
- Add write-metadata to cloud_init_modules

* Fri Jul 25 2014 Ian Weller <iweller@amazon.com>
- Add write-metadata module

* Wed Jul 23 2014 Andrew Jorgensen <ajorgens@amazon.com>
- cloud-final runs despite start priority change

* Sat Jun 14 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Move the resetpriorities triggerpostun later in the scriptlets

* Thu Jun 12 2014 Dennis Gilmore <dennis@ausil.us> - 0.7.5-6
- fix typo in settings.py preventing metadata being fecthed in ec2

* Mon Jun  9 2014 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.5-5
- Stopped calling ``udevadm settle'' with --quiet since systemd 213 removed it

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Jun  2 2014 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.5-3
- Make dmidecode dependency arch-dependent [RH:1025071 RH:1067089]

* Mon Jun  2 2014 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.2-9
- Write /etc/locale.conf instead of /etc/sysconfig/i18n [RH:1008250]
- Add tmpfiles.d configuration for /run/cloud-init [RH:1103761]
- Use the license rpm macro
- BuildRequire python-setuptools, not python-setuptools-devel

* Fri May 30 2014 Matthew Miller <mattdm@fedoraproject.org> - 0.7.5-2
- add missing python-jsonpatch dependency [RH:1103281]

* Fri May 2 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Move cloud-final to near the end of the boot process

* Tue Apr 29 2014 Sam Kottler <skottler@fedoraproject.org> - 0.7.5-1
- Update to 0.7.5 and remove patches which landed in the release

* Wed Apr 23 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Cleanup whitespace in defaults config
- Move defaults.cfg to 00_defaults.cfg to make it easier to override defaults
- Default resize_rootfs to noblock
- Add ecdsa to ssh_genkeytypes

* Tue Apr 8 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Move preserve_hostname: true to the main config only

* Mon Apr 7 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Exclude only kernel from upgrades, not kernel*

* Fri Apr 4 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Complete cloud-init run if cloud-init upgrades itself from 0.5
- don't Require rsyslog

* Wed Apr 2 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Use set-defaults to block remaining modules on upgrade, migrate user-scripts, and use legacy sudoers file

* Thu Mar 27 2014 Tom Kirchner <tjk@amazon.com>
- Default to preserving hostname

* Thu Mar 20 2014 Ethan Faust <efaust@amazon.com>
- Remove prettytable dependency

* Wed Mar 19 2014 Ethan Faust <efaust@amazon.com>
- Add fallback repo endpoint of amazonaws.com

* Mon Mar 17 2014 Ethan Faust <efaust@amazon.com>
- Determine services domain dynamically

* Wed Mar 12 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Complete improvements to migrator module
- Also migrate semaphores when upgrading from < 0.7

* Tue Mar 11 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Use file logging instead of syslog
- Use triggers to migrate to new sysv names

* Thu Mar 6 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Fail softer on exceptions fetching #include data
- Refresh Amazon patchset
- Various fixes for logging

* Wed Mar 5 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Disable selinux support for now, and remove Require on policycoreutils and dmidecode

* Thu Feb 27 2014 Andrew Jorgensen <ajorgens@amazon.com>
- Update Amazon patches

* Fri Feb 21 2014 Andrew Jorgensen <ajorgens@amazon.com>
- First pass at rebase onto 0.7.x

* Mon Feb 3 2014 Andrew Jorgensen <ajorgens@amazon.com>
- import source package F20/cloud-init-0.7.2-7.fc20

* Sat Jan 25 2014 Sam Kottler <skottler@fedoraproject.org> - 0.7.2-8
- Remove patch to the Puppet service unit nane [RH:1057860]

* Tue Sep 24 2013 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.2-7
- Dropped xfsprogs dependency [RH:974329]

* Tue Sep 24 2013 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.2-6
- Added yum-add-repo module

* Fri Sep 20 2013 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.2-5
- Fixed puppet agent service name [RH:1008250]
- Let systemd handle console output [RH:977952 LP:1228434]
- Fixed restorecon failure when selinux is disabled [RH:967002 LP:1228441]
- Fixed rsyslog log filtering
- Added missing modules [RH:966888]

* Wed Sep 4 2013 Andrew Jorgensen <ajorgens@amazon.com>
- import source package F19/cloud-init-0.7.2-1.fc19

* Tue Aug 20 2013 Andrew Jorgensen <ajorgens@amazon.com>
- import source package RHEL6/cloud-init-0.7.1-2.el6
- setup complete for package cloud-init

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sat Jun 15 2013 Matthew Miller <mattdm@fedoraproject.org> - 0.7.2-3
- switch ec2-user to "fedora" --  see bugzilla #971439. To use another
  name, use #cloud-config option "users:" in userdata in cloud metadata
  service
- add that user to systemd-journal group

* Fri May 17 2013 Steven Hardy <shardy@redhat.com> - 0.7.2
- Update to the 0.7.2 release

* Thu May 02 2013 Steven Hardy <shardy@redhat.com> - 0.7.2-0.1.bzr809
- Rebased against upstream rev 809, fixes several F18 related issues
- Added dependency on python-requests

* Sat Apr  6 2013 Orion Poplawski <orion@cora.nwra.com> - 0.7.1-4
- Don't ship tests

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Dec 13 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.1-2
- Added default_user to cloud.cfg (this is required for ssh keys to work)

* Wed Nov 21 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.1-1
- Rebased against version 0.7.1
- Fixed broken sudoers file generation
- Fixed "resize_root: noblock" [LP:1080985]

* Tue Oct  9 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.0-1
- Rebased against version 0.7.0
- Fixed / filesystem resizing

* Sat Sep 22 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.0-0.3.bzr659
- Added dmidecode dependency for DataSourceAltCloud

* Sat Sep 22 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.0-0.2.bzr659
- Rebased against upstream rev 659
- Fixed hostname persistence
- Fixed ssh key printing
- Fixed sudoers file permissions

* Mon Sep 17 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 0.7.0-0.1.bzr650
- Rebased against upstream rev 650
- Added support for useradd --selinux-user

* Thu Sep 13 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.3-0.5.bzr532
- Use a FQDN (instance-data.) for instance data URL fallback [RH:850916 LP:1040200]
- Shut off systemd timeouts [RH:836269]
- Send output to the console [RH:854654]

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.3-0.4.bzr532
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jun 27 2012 Pádraig Brady <P@draigBrady.com> - 0.6.3-0.3.bzr532
- Add support for installing yum packages

* Sat Mar 31 2012 Andy Grimm <agrimm@gmail.com> - 0.6.3-0.2.bzr532
- Fixed incorrect interpretation of relative path for
  AuthorizedKeysFile (BZ #735521)

* Mon Mar  5 2012 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.3-0.1.bzr532
- Rebased against upstream rev 532
- Fixed runparts() incompatibility with Fedora

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.2-0.8.bzr457
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Oct  5 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.7.bzr457
- Disabled SSH key-deleting on startup

* Wed Sep 28 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.6.bzr457
- Consolidated selinux file context patches
- Fixed cloud-init.service dependencies
- Updated sshkeytypes patch
- Dealt with differences from Ubuntu's sshd

* Sat Sep 24 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.5.bzr457
- Rebased against upstream rev 457
- Added missing dependencies

* Fri Sep 23 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.4.bzr450
- Added more macros to the spec file

* Fri Sep 23 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.3.bzr450
- Fixed logfile permission checking
- Fixed SSH key generation
- Fixed a bad method call in FQDN-guessing [LP:857891]
- Updated localefile patch
- Disabled the grub_dpkg module
- Fixed failures due to empty script dirs [LP:857926]

* Fri Sep 23 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.2.bzr450
- Updated tzsysconfig patch

* Wed Sep 21 2011 Garrett Holmstrom <gholms@fedoraproject.org> - 0.6.2-0.1.bzr450
- Initial packaging
