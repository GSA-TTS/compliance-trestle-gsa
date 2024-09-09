# compliance-trestle-gsa

A plugin for [compliance-trestle](https://github.com/oscal-compass/compliance-trestle) to provide functionality specific to building and validating GSA IT SSPPs.

The easiest way to use compliance-trestle-gsa is via [docker-trestle](https://github.com/gsa-tts/docker-trestle) which has utilized these commands within the helper scripts.

## Installation

`pip install git+https://github.com/gsa-tts/compliance-trestle-gsa`

## Usage

### Validation

To validate that an SSP document contains the fields required for rendering a GSA IT SSPP:

`$ trestle gsa-validate -f path/to/ssp.json`

This command words for decomposed models or those in single files.

### Defaults

To add boilerplate entries to an existing SSP in order to pass `gsa-validate` you can use:

`$ trestle gsa-defaults -f path/to/ssp.json`

This command requires that the SSP has been merged into the single file before you run the command.
