# Code is derived from clinspacy https://github.com/ML4LHS/clinspacy/blob/master/LICENSE.md#mit-license
#
# Some useful keyboard shortcuts for package authoring:
#
#   Install Package:           'Ctrl + Shift + B'
#   Check Package:             'Ctrl + Shift + E'
#   Test Package:              'Ctrl + Shift + T'

# spacy <- NULL
# scispacy <- NULL
# negspacy <- NULL
# nlp <- NULL
# negex <- NULL
# linker <- NULL

miscnlp_env = new.env(parent = emptyenv())

.onLoad <- function(libname, pkgname) {
  reticulate::configure_environment(force = TRUE)
}

.onAttach <- function(libname, pkgname) {
  packageStartupMessage('Welcome to miscnlp.')
  packageStartupMessage('By default, this package will install and use miniconda and create a "miscnlp" conda environment.')
  packageStartupMessage('If you want to override this behavior, use miscnlp_init(miniconda = FALSE) and specify an alternative environment using reticulate::use_python() or reticulate::use_conda().')
}


#' Initializes miscnlp. This function is optional to run but gives you more
#' control over the parameters. If you do not run
#' this function, it will be run with default parameters the first time that any
#' of the package functions are run.
#'
#' @param miscnlp_dir directory name of where misc_nlp github project is installed -- e.g. /Users/me/dev/misc_nlp
#' @param miniconda Defaults to TRUE, which results in miniconda being installed
#'   (~400 MB) and configured with the "miscnlp" conda environment. If you
#'   want to override this behavior, set \code{miniconda} to \code{FALSE} and
#'   specify an alternative environment using use_python() or use_conda().
#' @param update_miscnlp Defaults to FALSE. If true, the entire miscnlp package will be downloaded again.
#'
#' @return No return value.
#'
#' @export
miscnlp_init <- function(miscnlp_dir, miniconda = TRUE, update_miscnlp = FALSE) {

  assertthat::assert_that(assertthat::is.flag(miniconda))
  assertthat::assert_that(assertthat::is.flag(update_miscnlp))

  if (miniconda) {
    message('Checking if miniconda is installed...')
    tryCatch(reticulate::install_miniconda(),
             error = function (e) {return()})

    # By now, miniconda should be installed. Let's check if the miscnlp environment is configured
    is_miscnlp_env_installed = tryCatch(reticulate::use_miniconda(condaenv = 'miscnlp', required = TRUE),
                                          error = function (e) {'not installed'})

    if (!is.null(is_miscnlp_env_installed)) { # this means the 'miscnlp' condaenv *is not* installed
      message('miscnlp requires the miscnlp conda environment. Attempting to create...')
      reticulate::conda_create(envname = 'miscnlp', python_version = '3.9')
    }

    # This is intentional -- will throw an error if environment creation failed
    reticulate::use_miniconda(condaenv = 'miscnlp', required = TRUE)
  }

  # ignore_installed is used throughout the code below because the versions matter.
  # e.g. pyrush 1.4 was causing the package to fail so we need to force 1.3.5 even if 1.4 is already downloaded somewhere.

  if (!reticulate::py_module_available('spacy')) {
    message('SpaCy not found. Installing requests first...')
    # Install requests first so that we do not get too new of a version as it causes problems with medspacy
    # Does not work if we install with spacy at the same time (maybe because not using pip for spacy?)
    reticulate::py_install('requests>=2.13.0,<=2.15', envname = 'miscnlp', pip = TRUE, ignore_installed = TRUE)
    message('SpaCy not found. Installing spaCy...')
    # Insist on holding back the requests verison
    # Do NOT install using pip because no binary available and build fails on Windows
    reticulate::py_install('spacy==3.1.3', envname = 'miscnlp')
  }

  if (!reticulate::py_module_available('medspacy')) {
    message('medspaCy not found. Installing medspaCy and dependencies...')
    # Need to fix pyrush installation version. Version 1.4 gives an error like:
    # "[E004] Can't set up pipeline component: a factory for 'medspacy_pyrush' already exists"
    # requests also has to stay in a certian range
    # Install a version that fixes the versions of libraries so there are no command line errors
    reticulate::py_install(c('requests>=2.13.0,<=2.15', 'pyrush==1.0.3.5', 'medspacy'), envname = 'miscnlp', pip = TRUE, ignore_installed = TRUE)
  }

  # Installs Python portion of miscnlp or updates the current installation if update_miscnlp is TRUE
  if (update_miscnlp || !reticulate::py_module_available('misc_nlp')) {
    if (!reticulate::py_module_available('misc_nlp')) {
      message('miscnlp not found. Installing misc_nlp...')
    } else {
      message('Attempting to update misc_nlp...')
    }
    # TODO switch to github when package is public
    # library(credentials)
    # credentials::set_github_pat()
    # token = credentials::git_credential_ask("https://github.com")
    # reticulate::py_install('git+https://github.com/JewlsIOB/miscnlp@v1.0.0', envname = 'miscnlp', pip = TRUE, pip_ignore_installed = update_miscnlp, auth_token = token)
    reticulate::py_install(c('requests>=2.13.0,<=2.15', 'pyrush==1.0.3.5', miscnlp_dir), envname = 'miscnlp', pip = TRUE, ignore_installed = TRUE)
  }

  # This version works with Spacy 3.1-3.2
  # https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.1.0
  # Other dictionaries can be downloaded and loaded as well
  if (!reticulate::py_module_available('en_core_web_sm')) {
    message('en_core_web_sm language model not found. Installing en_core_web_sm...')
    # Insist on holding back the requests verison
    reticulate::py_install(c('requests>=2.13.0,<=2.15', 'https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.1.0/en_core_web_sm-3.1.0.tar.gz#egg=en_core_web_sm'), envname = 'miscnlp', pip = TRUE)
  }

  message('Importing python misc_nlp project...')
  miscnlp_env$misc_nlp <- reticulate::import('misc_nlp', delay_load = TRUE)

  invisible()
}
