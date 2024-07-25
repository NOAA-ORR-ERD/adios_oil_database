
function branch_exists_locally() {
    local branch=${1}
    local exists_locally=$(git rev-parse --verify ${branch} 2>/dev/null)

    if [[ -n ${exists_locally} ]]
    then
        echo 0
    else
        echo 1
    fi
}

function branch_exists_remotely() {
    local branch=${1}
    local exists_remotely=$(git ls-remote --heads origin ${branch})

    if [[ -n ${exists_remotely} ]]
    then
        echo 0
    else
        echo 1
    fi
}

function branch_exists() {
    local branch=${1}
    local exists_locally=$(git show-ref --quiet refs/heads/${branch})
    local exists_remotely=$(git ls-remote --heads origin ${branch})

    if [[ -n ${exists_locally} ]] || [[ -n ${exists_remotely} ]]
    then
        echo 0
    else
        echo 1
    fi
}
