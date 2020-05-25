# CrateDB

In order to get the CrateDB container working properly you have to set the `vm.max_map_count` to `262144` for systemd. This can be done by running

`sudo sysctl -w vm.max_map_count=262144`

As you can see in [CrateDB documentation](https://crate.io/docs/crate/howtos/en/latest/admin/bootstrap-checks.html#linux)
