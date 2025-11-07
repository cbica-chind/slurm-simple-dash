# slurm-simple-dash

Simple Slurm dashboard

## Installation

### Scripts

Copy 2 files to `/admin/bin`:

-   `slurm-simple-dash.py`
-   `slurm-simple-dash-wrapper.sh`

### Crontab

Must be on `infr4`.

Copy to `/etc/cron.d`:

-   `slurm_load`

### Symlink in web directory

In `/admin/centos7/httpd/var/www/html/slurm-load`:

``` console
$ ln -s cubic_load.html index.html
```
