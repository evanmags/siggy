# Siggy

Update your email with the latest tackle branded signature.

## Installation

```sh
# requires python 3.8+
pip install git+https://github.com/evanmags/siggy.git
```
## Usage

```sh
siggy config # enter details when prompted
siggy
```

## Development

```sh
brew install pyenv
pyenv install 3.10.5
pyenv virtualenv siggy
pyenv local siggy

pip install -r requirements.dev.txt
```

### To Do:
- [ ] put google credentials in secrets manager to load (currently not shared)
- [ ] signin to google with okta
- [ ] pull templates from a shared drive, rather than github?
