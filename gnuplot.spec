%define major 4
%define minor 2
%define patchlevel 6

%define x11_app_defaults_dir %{_datadir}/X11/app-defaults

%if %($(pkg-config emacs) ; echo $?)
%define emacs_version 22.1
%define emacs_lispdir %{_datadir}/emacs/site-lisp
%define emacs_startdir %{_datadir}/emacs/site-lisp/site-start.d
%else
%define emacs_version %(pkg-config emacs --modversion)
%define emacs_lispdir %(pkg-config emacs --variable sitepkglispdir)
%define emacs_startdir %(pkg-config emacs --variable sitestartdir)
%endif

Summary: A program for plotting mathematical expressions and data
Name: gnuplot
Version: %{major}.%{minor}.%{patchlevel}
Release: 2%{?dist}
# Modifications are to be distributed as patches to the released version.
License: gnuplot
Group: Applications/Engineering
URL: http://www.gnuplot.info/
Source: http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source2: gnuplot-init.el
Patch1: gnuplot-4.2.0-refers_to.patch
BuildRequires: libpng-devel, tex(latex), zlib-devel, libX11-devel, emacs
BuildRequires: texinfo, readline-devel, libXt-devel, gd-devel
BuildRequires: latex2html
Requires: %{name}-common = %{version}-%{release}
Requires(post): %{_sbindir}/alternatives
Requires(preun): %{_sbindir}/alternatives
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Gnuplot is a command-line driven, interactive function plotting
program especially suited for scientific data representation.  Gnuplot
can be used to plot functions and data points in both two and three
dimensions and in many different formats.

Install gnuplot if you need a graphics package for scientific data
representation.

%package common
Group: Applications/Engineering
Summary: common gnuplot parts
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

%description common
Gnuplot is a command-line driven, interactive function plotting
program especially suited for scientific data representation.  Gnuplot
can be used to plot functions and data points in both two and three
dimensions and in many different formats.

This subpackage contains common parts needed for arbitrary version of gnuplot

%package minimal
Group: Applications/Engineering
Summary: Minimal version of program for plotting mathematical expressions and data
Requires: %{name}-common = %{version}-%{release}
Requires(post): %{_sbindir}/alternatives
Requires(preun): %{_sbindir}/alternatives

%description minimal
Gnuplot is a command-line driven, interactive function plotting
program especially suited for scientific data representation.  Gnuplot
can be used to plot functions and data points in both two and three
dimensions and in many different formats.

Install gnuplot-minimal if you need a minimal version of graphics package 
for scientific data representation.

%package -n emacs-%{name}
Group: Applications/Engineering
Summary: Emacs bindings for the gnuplot main application
Requires: %{name} = %{version}-%{release}
BuildRequires:  emacs emacs-el pkgconfig
Requires: emacs >= %{emacs_version}
Provides: gnuplot-emacs = %{version}-%{release}
Obsoletes: gnuplot-emacs < 4.2.2-3

%description -n emacs-%{name}
The gnuplot-emacs package contains the emacs related .elc files so that gnuplot
nicely interacts and integrates into emacs.

%package -n emacs-%{name}-el
Group: Applications/Engineering
Summary: Emacs bindings for the gnuplot main application
Requires: emacs-%{name} = %{version}-%{release}
Obsoletes: gnuplot-emacs < 4.2.2-3

%description -n emacs-%{name}-el
The gnuplot-emacs package contains the emacs related .el files so that gnuplot
nicely interacts and integrates into emacs.

%package  doc
Group: Applications/Engineering
Summary: Documentation fo bindings for the gnuplot main application
Obsoletes: gnuplot-common < 4.2.4-5

%description doc
The gnuplot-doc package contains the documentation related to gnuplot 
plotting tool

%package  latex
Group: Applications/Engineering
Summary: Configuration for LaTeX typesetting using gnuplot
Requires: tex(latex)
Requires: %{name} = %{version}-%{release}
BuildArch: noarch
Obsoletes: gnuplot-common < 4.2.5-2

%description latex
The gnuplot-latex package contains LaTeX configuration file related to gnuplot 
plotting tool.


%prep
%setup -q
%patch1 -p1 -b .refto
sed -i -e 's:"/usr/lib/X11/app-defaults":"%{x11_app_defaults_dir}":' src/gplt_x11.c
iconv -f windows-1252 -t utf-8 ChangeLog > ChangeLog.aux
mv ChangeLog.aux ChangeLog
chmod 644 src/getcolor.h
chmod 644 demo/html/webify.pl

%build
# at first create minimal version of gnuplot for server SIG purposes
%configure --with-readline=gnu --with-png --without-linux-vga \
 --enable-history-file --disable-wxwidgets
make %{?_smp_mflags}
cp src/gnuplot src/gnuplot-minimal

## clean all settings
#make clean
## create full version of gnuplot
#%configure --with-readline=gnu --with-png --without-linux-vga \
# --enable-history-file
#make %{?_smp_mflags}

cd docs
make html
cd psdoc
export GNUPLOT_PS_DIR=../../term/PostScript
make ps_symbols.ps ps_fontfile_doc.pdf
cd ../..
rm -rf docs/htmldocs/images.idx

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT INSTALL='install -p'
install -d ${RPM_BUILD_ROOT}%{_datadir}/emacs/site-lisp/site-start.d/
install -p -m 644 %SOURCE2 ${RPM_BUILD_ROOT}%{_datadir}/emacs/site-lisp/site-start.d/gnuplot-init.el
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/info-look*.el*
install -d ${RPM_BUILD_ROOT}%{_datadir}/emacs/site-lisp/gnuplot
mv $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/gnuplot.el{,c} $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/gnuplot
mv $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/gnuplot-gui.el{,c} $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/gnuplot

mkdir -p $RPM_BUILD_ROOT%{x11_app_defaults_dir}
mv $RPM_BUILD_ROOT%{_libdir}/X11/app-defaults/Gnuplot $RPM_BUILD_ROOT%{x11_app_defaults_dir}/Gnuplot
rm -rf $RPM_BUILD_ROOT%{_libdir}/

# rename binary
mv $RPM_BUILD_ROOT%{_bindir}/gnuplot $RPM_BUILD_ROOT%{_bindir}/gnuplot-wx
# install minimal binary
install -p -m 755 ./src/gnuplot-minimal $RPM_BUILD_ROOT%{_bindir}/gnuplot-minimal

%posttrans
%{_sbindir}/alternatives --install %{_bindir}/gnuplot gnuplot %{_bindir}/gnuplot-wx 60

%post common
if [ -f %{_infodir}/gnuplot.info* ]; then
    /sbin/install-info %{_infodir}/gnuplot.info %{_infodir}/dir || :
fi

%posttrans minimal
%{_sbindir}/alternatives --install %{_bindir}/gnuplot gnuplot %{_bindir}/gnuplot-minimal 40

%preun
if [ $1 = 0 ]; then
    %{_sbindir}/alternatives --remove gnuplot %{_bindir}/gnuplot-wx || :
fi

%preun common
if [ $1 = 0 ] ; then # last uninstall
    if [ -f %{_infodir}/gnuplot.info* ]; then
	/sbin/install-info --delete %{_infodir}/gnuplot.info %{_infodir}/dir || :
    fi
fi

%preun minimal
if [ $1 = 0 ]; then
    %{_sbindir}/alternatives --remove gnuplot %{_bindir}/gnuplot-minimal || :
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_bindir}/gnuplot-wx

%files doc
%defattr(-,root,root,-)
%doc ChangeLog Copyright
%doc docs/psdoc/ps_guide.ps docs/psdoc/ps_symbols.ps tutorial/tutorial.dvi demo docs/psdoc/ps_file.doc
%doc docs/psdoc/ps_fontfile_doc.pdf docs/htmldocs tutorial/eg7.eps

%files common
%defattr(-,root,root,-)
%doc BUGS ChangeLog Copyright FAQ NEWS README TODO
%{_mandir}/man1/gnuplot.1.gz
%dir %{_datadir}/gnuplot
%dir %{_datadir}/gnuplot/%{major}.%{minor}
%dir %{_datadir}/gnuplot/%{major}.%{minor}/PostScript
%{_datadir}/gnuplot/%{major}.%{minor}/PostScript/*.ps
%{_datadir}/gnuplot/%{major}.%{minor}/gnuplot.gih
%dir %{_libexecdir}/gnuplot
%dir %{_libexecdir}/gnuplot/%{major}.%{minor}
%{_libexecdir}/gnuplot/%{major}.%{minor}/gnuplot_x11
%{x11_app_defaults_dir}/Gnuplot
%{_infodir}/gnuplot.info.gz

%files minimal
%defattr(-,root,root,-)
%{_bindir}/gnuplot-minimal

%files -n emacs-%{name}
%defattr(-,root,root,-)
%doc ChangeLog Copyright
%dir %{emacs_lispdir}/%{name}
%{emacs_lispdir}/%{name}/*.elc
%{emacs_startdir}/*.el

%files -n emacs-%{name}-el
%defattr(-,root,root,-)
%doc ChangeLog Copyright
%{emacs_lispdir}/%{name}/*.el

%files latex
%defattr(-,root,root,-)
%dir %{_datadir}/texmf/tex/latex/gnuplot
%{_datadir}/texmf/tex/latex/gnuplot/gnuplot.cfg

%changelog
* Mon Feb 22 2010 Ivana Hutarova Varekova <varekova@redhat.com> 4.2.6-2 
- Resolves: #564090
  don't use wxGTK in gnuplot
  licence tag fix

* Tue Sep 15 2009 Ivana Varekova <varekova@redhat.com> 4.2.6-1
- update to 4.2.6

* Mon Aug 10 2009 Ivana Varekova <varekova@redhat.com> 4.2.5-6
- fix installation with --excludedocs option (#515963)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.5-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jun 15 2009 Ivana Varekova <varekova@redhat.com> - 4.2.5-4
- add gnuplot-latex subpackage
  patch by jnovy

* Fri May 29 2009 Ivana Varekova <varekova@redhat.com> - 4.2.5-2
- fix preun scripts

* Thu May 28 2009 Ivana Varekova <varekova@redhat.com> - 4.2.5-1
- update to 4.2.5

* Fri Mar 27 2009 Ivana Varekova <varekova@redhat.com> - 4.2.4-6
- split documentation

* Tue Mar 10 2009 Ivana Varekova <varekova@redhat.com> - 4.2.4-5
- fix #489069 (update of the package from nonsplit version
  causes the absence of gnuplot binary -
  fixed using posttrans instead of post)

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jan 14 2009 Ivana Varekova <varekova@redhat.com> - 4.2.4-3
- fix sbin path

* Tue Jan 13 2009 Ivana Varekova <varekova@redhat.com> - 4.2.4-2
- add minimal package for server SIG purposes

* Fri Nov  7 2008 Ivana Varekova <varekova@redhat.com> - 4.2.4-1
- update to 4.2.4

* Fri May  9 2008 Ivana Varekova <varekova@redhat.com> - 4.2.3-1
- update to 4.2.3

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 4.2.2-10
- Autorebuild for GCC 4.3

* Tue Jan 29 2008 Ivana Varekova <varekova@redhat.com> - 4.2.2-9
- spec file cleanup

* Mon Jan 28 2008 Ivana Varekova <varekova@redhat.com> - 4.2.2-8
- fix 430335 - add wxGTK requires

* Mon Dec 10 2007 Ivana Varekova <varekova@redhat.com> - 4.2.2-7
- add wxGTK-devel dependency (#405411)

* Thu Nov 15 2007 Ivana Varekova <varekova@redhat.com> - 4.2.2-6
- add obsoletes tag

* Mon Nov 12 2007 Ivana Varekova <varekova@redhat.com> - 4.2.2-5
- fix 373941 - add provides tag

* Tue Nov  6 2007 Ivana Varekova <varekova@redhat.com> - 4.2.2-4
- fix webify.pl permissions
- add eg7.eps to documentation

* Thu Nov  1 2007 Ivana Varekova <varekova@redhat.com> - 4.2.2-3
- add emacs buildrequires
- add emacs-* macros
- remove useless iconv

* Thu Oct 25 2007 Ivana Varekova <varekova@redhat.com> - 4.2.2-2
- rename emacs subpackage, split intwo two parts
- add font directories
- clean spec file

* Thu Oct 25 2007 Ivana Varekova <varekova@redhat.com> - 4.2.2-1
- update to 4.2.2

* Wed Oct 17 2007 Ivana Varekova <varekova@redhat.com> - 4.2.0-7
- add URL tag

* Mon Sep 24 2007 Ivana Varekova <varekova@redhat.com> - 4.2.0-6
- spec file cleanup

* Fri Sep  7 2007 Ivana Varekova <varekova@redhat.com> - 4.2.0-5
- move emacs files to */site-lisp/gnuplot subdirectory

* Thu Sep  6 2007 Ivana Varekova <varekova@redhat.com> - 4.2.0-4
- change font paths, change documenatation

* Tue Aug 28 2007 Ivana Varekova <varekova@redhat.com> - 4.2.0-3
- Rebuild for selinux ppc32 issue.
- Remove obsolete file

* Tue Jul  3 2007 Ivana Varekova <varekova@redhat.com> - 4.2.0-2
- Resolves: #246316
  remove info-look.20.{2,3}.el

* Mon May 21 2007 Ivana Varekova <varekova@redhat.com> - 4.2.0-1
- Resolves: #231205
  update to 4.2.0
  spec changes from Tim Orling  

* Mon Mar 26 2007 Ivana Varekova <varekova@redhat.com> - 4.0.0-18
- add missing directories (#233838)

* Thu Mar 15 2007 Ivana Varekova <varekova@redhat.com> - 4.0.0-17
- incorporate the package review feedback

* Mon Jan 22 2007 Ivana Varekova <varekova@redhat.com> - 4.0.0-16
- Resolves: 223693  
  fix non-failsafe install-info problem

* Fri Dec 22 2006 Ivana Varekova <varekova@redhat.com> - 4.0.0-15
- Resolves: 173752
  gnuplot refers to /usr/X11R6/lib/fonts/Type1

* Tue Dec 21 2006 Ivana Varekova <varekova@redhat.com> - 4.0.0-14
- remove --without-gd options (#173922, #172565)
- spec file cleanup

* Fri Dec  1 2006 Ivana Varekova <varekova@redhat.com> - 4.0.0-13
- rebuild against libncurses

* Wed Jul 26 2006 Jesse Keating <jkeating@redhat.com> - 4.0.0-12
- rebuild

* Wed Mar 01 2006 Karsten Hopp <karsten@redhat.de> 4.0.0-11
- BuildRequires: libXt-devel

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 4.0.0-10.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 4.0.0-10.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Nov 02 2005 Phil Knirsch <pknirsch@redhat.com> 4.0.0-10
- Switched BuildPreReqs and Requires to modular xorg-x11 style

* Fri Oct 21 2005 Phil Knirsch <pknirsch@redhat.com> 4.0.0-9
- Fixed 64bit problem with x11 display (#167508)
- Added missing file ownage of /usr/share/gnuplot (#169333)

* Fri Sep 02 2005 Phil Knirsch <pknirsch@redhat.com> 4.0.0-8
- Fixed missing Requires: emacs for the gnuplot-emacs package
- Added a gnuplot-init.el file for startup (#151122)

* Wed Mar 02 2005 Phil Knirsch <pknirsch@redhat.com> 4.0.0-7
- bump release and rebuild with gcc 4

* Wed Jan 12 2005 Tim Waugh <twaugh@redhat.com> 4.0.0-6
- Rebuilt for new readline.

* Thu Dec 23 2004 Phil Knirsch <pknirsch@redhat.com> 4.0.0-5
- Added BUGS ChangeLog Copyright FAQ NEWS README TODO to docs (#139070)

* Mon Oct 11 2004 Tim Waugh <twaugh@redhat.com> 4.0.0-4
- Build requires texinfo and readline-devel (bug #134922)

* Tue Sep 07 2004 Karsten Hopp <karsten@redhat.de> 4.0.0-3 
- fix typo in preun script

* Thu Sep  2 2004 Bill Nottingham <notting@redhat.com> 4.0.0-2
- %%defattr fixes (#131640)

* Thu Aug 12 2004 Phil Knirsch <pknirsch@redhat.com> 4.0.0-1
- Update to gnuplot-4.0.0
- Split off emacs files into new subpackage

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jul 02 2003 Bill Nottingham <notting@redhat.com> 3.7.3-4
- fix license (#98449)

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Jan 21 2003 Bill Nottingham <notting@redhat.com> 3.7.3-1
- update to 3.7.3
- don't bother patching it to do jpegs with gd instead of gifs,
  as we haven't been building it with gd support anyway

* Fri Nov 29 2002 Tim Powers <timp@redhat.com> 3.7.2-2
- remove unpackaged files from the buildroot

* Thu Jul 18 2002 Bill Nottingham <notting@redhat.com> 3.7.2-1
- update to 3.7.2

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Feb 21 2002 Bill Nottingham <notting@redhat.com>
- rebuild

* Wed Jan 23 2002 Bill Nottingham <notting@redhat.com> 3.7.1-16
- fix bug #43620 (<broeker@physik.rwth-aachen.de>)

* Tue Jan 22 2002 Bill Nottingham <notting@redhat.com> 3.7.1-15
- fix bug #21341 (<wtcorrea@cs.princeton.edu>)

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Fri May 11 2001 Bernhard Rosenkraenzer <bero@redhat.com> 3.7.1-13
- rebuild with new readline
- Fix up License: and URL: tags in specfile

* Tue Aug 22 2000 Bill Nottingham <notting@redhat.com>
- remove zlib-devel requirement (#16718)

* Wed Aug 02 2000 Trond Eivind Glomsrød <teg@redhat.com>
- rebuild with libpng 1.0.8

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Mon Jun 18 2000 Bill Nottingham <notting@redhat.com>
- fix  manpage paths

* Fri Jun  9 2000 Bill Nottingham <notting@redhat.com>
- rebuild in new environment

* Fri May 19 2000 Nalin Dahyabhai <nalin@redhat.com>
- rebuild with new gd, changing gif terminal to jpeg terminal (release 7)

* Mon May 08 2000 Preston Brown <pbrown@redhat.com>
- build for 7.0

* Thu Apr  6 2000 Bill Nottingham <notting@redhat.com>
- use gnu readline, not built-in version

* Mon Apr  3 2000 Bill Nottingham <notting@redhat.com>
- add latex tutorial, demo files, other docs (#10508)

* Wed Mar  1 2000 Bill Nottingham <notting@redhat.com>
- update to 3.7.1. Oops.

* Thu Feb  3 2000 Bill Nottingham <notting@redhat.com>
- handle compressed man pages

* Thu Nov  4 1999 Bill Nottingham <notting@redhat.com>
- update to 3.7.1

* Mon Oct 11 1999 Bill Nottingham <notting@redhat.com>
- ship some docs.

* Wed Aug 18 1999 Bill Nottingham <notting@redhat.com>
- add a patch to fix postscript output from Bernd Kischnick
 (kisch@die-herrmanns.de)

* Fri Jul 30 1999 Bill Nottingham <notting@redhat.com>
- fix license

* Thu Jul 15 1999 Bill Nottingham <notting@redhat.com>
- rebuild without svgalib

* Tue Jun 15 1999 Bill Nottingham <notting@redhat.com>
- update to 3.7.0.1

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 2)

* Tue Feb  2 1999 Jeff Johnson <jbj@redhat.com>
- update to 3.7.

* Thu Dec 17 1998 Michael Maher <mike@redhat.com>
- built package for 6.0

* Fri Sep 11 1998 Jeff Johnson <jbj@redhat.com>
- update to 2.6beta347

* Sat Aug 15 1998 Jeff Johnson <jbj@redhat.com>
- build root

* Thu May 07 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Mon Oct 20 1997 Donnie Barnes <djb@redhat.com>
- spec file cleanups

* Thu Jul 10 1997 Erik Troan <ewt@redhat.com>
- built against glibc
