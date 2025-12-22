#!/bin/bash

# Get directory of this script
if [[ -n "${BASH_SOURCE[0]}" ]]; then
    SCRIPT_PATH="${BASH_SOURCE[0]}"
elif [[ -n "${ZSH_VERSION}" ]]; then
    SCRIPT_PATH="${(%):-%x}"
else
    SCRIPT_PATH="$0"
fi

BASE_DIR="$( cd "$( dirname "$SCRIPT_PATH" )" && pwd )"
CLASHPP_PY="$BASE_DIR/clashpp.py"

# Default Runner
RUNNER=("python3")

# Detect overrides from env or args
# We need to parse --python explicitly from arguments intended for functions or direct execution
CUSTOM_PYTHON=""

function _parse_args() {
    local args=()
    while [[ $# -gt 0 ]]; do
        case $1 in
            --python)
                CUSTOM_PYTHON="$2"
                shift # past argument
                shift # past value
                ;;
            *)
                args+=("$1")
                shift # past argument
                ;;
        esac
    done
    echo "${args[@]}"
}

function _clashpp_exec() {
    # Parse --python from args first
    # This is tricky in bash function wrapper because we want to consume --python 
    # but pass the rest to the python script.
    
    # Check if user provided python path via args
    local py_cmd
    py_cmd=("${RUNNER[@]}")
    local script_args=()
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --python)
                py_cmd=("$2")
                shift 2
                ;;
            *)
                script_args+=("$1")
                shift
                ;;
        esac
    done

    "${py_cmd[@]}" "$CLASHPP_PY" "${script_args[@]}"
}

function clashpp() {
    _clashpp_exec "$@"
}

function clashon() {
    echo "Starting Clashpp..."
    # We need to pass $@ to clashpp to allow --python override if user does `clashon --python ...`
    # But wait, clashon calls `clashpp start`. We need to inject --python before `start` if present?
    # Or just let clashpp handle it?
    # Our python script doesn't know --python. So we must strip it in the shell wrapper.
    
    # Simple way: just forward all args to clashpp wrapper which parses --python
    # But we need to ensure 'start' is passed.
    
    
    # Check for help argument
    for arg in "$@"; do
        if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
             _clashpp_exec start --help
             return 0
        fi
    done
    
    _clashpp_exec start "$@"
    if [ $? -eq 0 ]; then
        # For env, we also need to respect the python path if set in the previous call? 
        # Ideally, it shouldn't matter for 'env' since it just reads a file, but for consistency:
        # We can re-use the runner logic. But `clashpp env` needs the same args from $@ if --python is there.
        eval "$(_clashpp_exec env "$@")"
        echo "Proxy environment variables exported."
    fi
}

function clashoff() {
    echo "Stopping Clashpp..."
    _clashpp_exec stop "$@"
    unset http_proxy
    unset https_proxy
    unset all_proxy
    echo "Proxy environment variables unset."
}

function clashui() {
    _clashpp_exec status "$@"
}

function clashupdate() {
    _clashpp_exec update "$@"
}

function clashinstall() {
    _clashpp_exec install "$@"
}

function _clashpp_help() {
    echo "Clashpp - Portable Rootless Proxy Manager"
    echo ""
    echo "Usage (Sourced Mode):"
    echo "  source clashpp.sh"
    echo "  clashon       [--python PATH]  Start proxy"
    echo "  clashoff      [--python PATH]  Stop proxy"
    echo "  clashui       [--python PATH]  Show status"
    echo "  clashupdate   [--python PATH]  Update subscription/kernel"
    echo ""
    echo "Usage (Direct Mode):"
    echo "  bash clashpp.sh install [--python PATH]   Install kernel"
    echo "  bash clashpp.sh --help                    Show this message"
    echo ""
}

# Direct execution handling
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # We need to parse command vs args.
    # $1 might be "install" or "--python"
    
    # Let's peek at $1
    case "$1" in
        --help|-h)
            _clashpp_help
            exit 0
            ;;
    esac
    
    # We pass everything to clashpp wrapper, but we need to supply the COMMAND if it's implicit?
    # No, direct execution usually expects subcommands like 'install'.
    
    # If user does `bash clashpp.sh install --python /bin/python`
    # $1=install, $2=--python...
    # clashpp wrapper will parse --python and run `python clashpp.py install`
    
    _clashpp_exec "$@"
fi
