utctimestamp() {
    date -u +'%Y-%m-%dT%H:%M:%SZ'
}

log() {
    echo -e "\033[34m$(date +'%Y/%m/%d %H:%M:%S') - $*\033[0m"
}

fatal() {
    echo -e "\033[31m$(date +'%Y/%m/%d %H:%M:%S') - $*\033[0m"
    exit 1
}

partuuid() {
    if ! blkid -s UUID -o value "$1"; then
        fatal "failed to get partition uuid for $1"
    fi
}

download_file() {
    if test -e "$2"; then
        log "skipping download. $2 already exists"
    else
        log "downloading $1 to $2"
        if ! wget "$1" -O "$2"; then
            fatal "failed to download $1"
        fi
    fi
}

erase_disk() {
    log "erasing disk $1"
    if ! dd if=/dev/zero of="$1" bs=1M count=32 && sync; then
        fatal "failed to erase disk $1"
    fi
}

# expects fdisk input on stdio
partition_disk() {
    log "partitioning disk $1"
    fdisk $disk && sync && partprobe
}

# expects fdisk input on stdio
setup_disk() {
    erase_disk "$1"
    partition_disk "$1"
    sleep 3
}
