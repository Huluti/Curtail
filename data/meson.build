bindir = join_paths(get_option('prefix'), get_option('bindir'))
datadir = join_paths(get_option('prefix'), get_option('datadir'))
pkgdatadir = join_paths(datadir, meson.project_name())

blueprints = custom_target('blueprints',
  input: files(
    'ui/preferences.blp',
    'ui/result-item-row.blp',
    'ui/shortcuts-dialog.blp',
    'ui/window.blp'
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome = import('gnome')

gnome.compile_resources('curtail',
  'curtail.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

desktop_conf = configuration_data()
desktop_conf.set('icon', application_id)
desktop_file = i18n.merge_file(
  input: configure_file(
    input: files('com.github.huluti.Curtail.desktop.in.in'),
    output: 'com.github.huluti.Curtail.desktop.in',
    configuration: desktop_conf,
  ),
  output: '@0@.desktop'.format(application_id),
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: get_option('datadir') / 'applications',
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

metainfo_conf = configuration_data()
metainfo_conf.set('appid', application_id)
appstream_file = i18n.merge_file(
  input: configure_file(
    input: files('com.github.huluti.Curtail.metainfo.xml.in.in'),
    output: 'com.github.huluti.Curtail.metainfo.xml.in',
    configuration: metainfo_conf
  ),
  output: '@0@.metainfo.xml'.format(application_id),
  po_dir: '../po',
  install: true,
  install_dir: get_option('datadir') / 'metainfo',
)

appstreamcli = find_program('appstreamcli', required: false)
if (appstreamcli.found())
  test('Validate metainfo file',
    appstreamcli,
    args: ['validate', '--no-net', '--explain', appstream_file],
    workdir: meson.current_build_dir()
  )
endif

install_data('com.github.huluti.Curtail.gschema.xml',
  rename: '@0@.gschema.xml'.format(application_id),
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

service_conf = configuration_data()
service_conf.set('app-id', application_id)
service_conf.set('bindir', bindir)
configure_file(
  input: 'com.github.huluti.Curtail.service.in',
  output: '@0@.service'.format(application_id),
  configuration: service_conf,
  install_dir: join_paths(get_option('datadir'), 'dbus-1', 'services')
)

subdir('icons')
