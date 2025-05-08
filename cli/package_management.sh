#!/bin/bash

# Source common functions
source "$(dirname "$0")/functions.sh"

# Package management functions

# Install a package using the appropriate package manager
install_package() {
    local package="$1"
    local manager="$2"
    local options="$3"
    
    log_info "Installing package $package using $manager"
    
    case "$manager" in
        "apt")
            if [ -z "$options" ]; then
                sudo apt-get install -y "$package"
            else
                sudo apt-get install -y $options "$package"
            fi
            ;;
        "pip")
            if [ -z "$options" ]; then
                pip install "$package"
            else
                pip install $options "$package"
            fi
            ;;
        "pip3")
            if [ -z "$options" ]; then
                pip3 install "$package"
            else
                pip3 install $options "$package"
            fi
            ;;
        "npm")
            if [ -z "$options" ]; then
                yes | npm install "$package"
            else
                yes | npm install $options "$package"
            fi
            ;;
        "npx")
            if [ -z "$options" ]; then
                npx "$package"
            else
                npx $options "$package"
            fi
            ;;
        "dpkg")
            if [ -z "$options" ]; then
                sudo dpkg -i "$package"
            else
                sudo dpkg $options "$package"
            fi
            ;;
        *)
            log_error "Unsupported package manager: $manager"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        log_success "Successfully installed $package"
        return 0
    else
        log_error "Failed to install $package"
        return 1
    fi
}

# Uninstall a package using the appropriate package manager
uninstall_package() {
    local package="$1"
    local manager="$2"
    local options="$3"
    
    log_info "Uninstalling package $package using $manager"
    
    case "$manager" in
        "apt")
            if [ -z "$options" ]; then
                sudo apt-get remove -y "$package"
            else
                sudo apt-get remove -y $options "$package"
            fi
            ;;
        "pip")
            if [ -z "$options" ]; then
                pip uninstall -y "$package"
            else
                pip uninstall -y $options "$package"
            fi
            ;;
        "pip3")
            if [ -z "$options" ]; then
                pip3 uninstall -y "$package"
            else
                pip3 uninstall -y $options "$package"
            fi
            ;;
        "npm")
            if [ -z "$options" ]; then
                yes | npm uninstall "$package"
            else
                yes | npm uninstall $options "$package"
            fi
            ;;
        "dpkg")
            if [ -z "$options" ]; then
                sudo dpkg -r "$package"
            else
                sudo dpkg -r $options "$package"
            fi
            ;;
        *)
            log_error "Unsupported package manager: $manager"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        log_success "Successfully uninstalled $package"
        return 0
    else
        log_error "Failed to uninstall $package"
        return 1
    fi
}

# Update package lists
update_package_lists() {
    local manager="$1"
    
    log_info "Updating package lists for $manager"
    
    case "$manager" in
        "apt")
            sudo apt-get update
            ;;
        "pip"|"pip3")
            log_info "No need to update package lists for $manager"
            return 0
            ;;
        "npm")
            npm update
            ;;
        *)
            log_error "Unsupported package manager: $manager"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        log_success "Successfully updated package lists for $manager"
        return 0
    else
        log_error "Failed to update package lists for $manager"
        return 1
    fi
}

# Upgrade packages
upgrade_packages() {
    local manager="$1"
    local package="$2"
    
    log_info "Upgrading packages for $manager"
    
    case "$manager" in
        "apt")
            if [ -z "$package" ]; then
                sudo apt-get upgrade -y
            else
                sudo apt-get install --only-upgrade -y "$package"
            fi
            ;;
        "pip")
            if [ -z "$package" ]; then
                pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
            else
                pip install -U "$package"
            fi
            ;;
        "pip3")
            if [ -z "$package" ]; then
                pip3 list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip3 install -U
            else
                pip3 install -U "$package"
            fi
            ;;
        "npm")
            if [ -z "$package" ]; then
                yes | npm update
            else
                yes | npm update "$package"
            fi
            ;;
        *)
            log_error "Unsupported package manager: $manager"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        log_success "Successfully upgraded packages for $manager"
        return 0
    else
        log_error "Failed to upgrade packages for $manager"
        return 1
    fi
}

# Check if a package is installed
is_package_installed() {
    local package="$1"
    local manager="$2"
    
    case "$manager" in
        "apt")
            dpkg -l "$package" &> /dev/null
            ;;
        "pip")
            pip show "$package" &> /dev/null
            ;;
        "pip3")
            pip3 show "$package" &> /dev/null
            ;;
        "npm")
            npm list -g "$package" &> /dev/null || npm list "$package" &> /dev/null
            ;;
        "dpkg")
            dpkg -l "$package" &> /dev/null
            ;;
        *)
            log_error "Unsupported package manager: $manager"
            return 1
            ;;
    esac
    
    return $?
}

# Get package version
get_package_version() {
    local package="$1"
    local manager="$2"
    
    case "$manager" in
        "apt")
            dpkg -l "$package" 2> /dev/null | grep "^ii" | awk '{print $3}'
            ;;
        "pip")
            pip show "$package" 2> /dev/null | grep "^Version:" | awk '{print $2}'
            ;;
        "pip3")
            pip3 show "$package" 2> /dev/null | grep "^Version:" | awk '{print $2}'
            ;;
        "npm")
            npm list -g "$package" 2> /dev/null | grep "$package@" | awk -F@ '{print $2}' || npm list "$package" 2> /dev/null | grep "$package@" | awk -F@ '{print $2}'
            ;;
        "dpkg")
            dpkg -l "$package" 2> /dev/null | grep "^ii" | awk '{print $3}'
            ;;
        *)
            log_error "Unsupported package manager: $manager"
            return 1
            ;;
    esac
    
    return $?
}

# Main function
main() {
    local command="$1"
    local package="$2"
    local manager="$3"
    local options="$4"
    
    case "$command" in
        "install")
            install_package "$package" "$manager" "$options"
            ;;
        "uninstall")
            uninstall_package "$package" "$manager" "$options"
            ;;
        "update")
            update_package_lists "$manager"
            ;;
        "upgrade")
            upgrade_packages "$manager" "$package"
            ;;
        "check")
            if is_package_installed "$package" "$manager"; then
                log_info "Package $package is installed"
                version=$(get_package_version "$package" "$manager")
                if [ -n "$version" ]; then
                    log_info "Version: $version"
                fi
                return 0
            else
                log_info "Package $package is not installed"
                return 1
            fi
            ;;
        *)
            echo "Usage: $0 [install|uninstall|update|upgrade|check] [package] [manager] [options]"
            echo "Managers: apt, pip, pip3, npm, npx, dpkg"
            return 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi