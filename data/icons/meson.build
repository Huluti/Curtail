icondir = join_paths('hicolor', 'scalable', 'apps')
install_data(
  join_paths(icondir, '@0@.svg'.format(application_id)),
  install_dir: join_paths(datadir, 'icons', icondir),
  rename: '@0@.svg'.format(application_id)
)

icondir = join_paths('hicolor', 'symbolic', 'apps')
install_data(
  join_paths(icondir, 'com.github.huluti.Curtail-symbolic.svg'),
  install_dir: join_paths(datadir, 'icons', icondir),
  rename: '@0@-symbolic.svg'.format(application_id)
)
