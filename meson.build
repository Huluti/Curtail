project('curtail',
          version: '1.17.0',
    meson_version: '>= 1.1.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')

profile = get_option('profile')
if profile == 'development'
  application_id = 'com.github.huluti.Curtail.Devel'
else
  application_id = 'com.github.huluti.Curtail'
endif

config_h = configuration_data()
config_h.set_quoted('APPLICATION_ID', application_id)
config_h.set_quoted('PROFILE', profile)
config_h.set_quoted('GETTEXT_PACKAGE', 'curtail')
config_h.set_quoted('PACKAGE_VERSION', meson.project_version())
configure_file(
   output: 'config.h',
   configuration: config_h,
)

configuration_inc = include_directories('.')

subdir('data')
subdir('src')
subdir('po')


gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)

summary({
  'Profile': get_option('profile'),
}, section: 'Development')
