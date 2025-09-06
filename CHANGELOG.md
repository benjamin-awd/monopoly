# Changelog

## [0.19.1] - 2025-09-06

### 🛠️ Bug Fixes

- *(banks/dbs)* Add metadata for new statement

### 📚 Documentation

- *(readme)* Update supported banks in README
- Sort supported banks alphabetically

### ⚙️ Miscellaneous Tasks

- *(banks/dbs)* Fix consolidated transaction pattern

### Build

- *(deps-dev)* Update pre-commit version

## [0.19.0] - 2025-08-06

### ⛰️ Features

- *(banks)* Add td canada trust
- *(multiline)* Multiline_transaction_date option
- *(banks)* Add CIBC
- *(banks)* Add Scotiabank
- *(credit)* Pre process transaction match
- *(banks)* Add Royal Bank of Canada ("RBC")
- *(banks)* Add Bank of Montreal ("BMO")
- *(banks)* Add Canadian Tire (credit only)
- *(banks)* Add Capital One Canada (credit only)

### 🛠️ Bug Fixes

- *(tdct)* Identifier for credit statement
- *(cibc)* Safety check can be performed
- *(bmo)* Statement date pattern
- *(tdct)* Credit transaction pattern

### 🚜 Refactor

- *(scotiabank)* Move credit transaction pattern
- *(tdct)* Merge "psuedo banks" into one
- *(canadian tire)* Move credit transaction pattern
- *(capital one canada)* Credit transaction pattern
- Standardize re.compile calls

### ⚙️ Miscellaneous Tasks

- Run linter to fix formatting
- Run linter & formatter

## [0.18.2] - 2025-06-14

### ⚙️ Miscellaneous Tasks

- Push missing amex safety check

## [0.18.1] - 2025-06-11

### 🚜 Refactor

- *(logs)* Allow pdf name in logs during verbose mode

### ⚙️ Miscellaneous Tasks

- Allow verbose logs during multi-threaded mode

## [0.18.0] - 2025-06-09

### ⛰️ Features

- *(banks)* Add limited support for SG Maybank credit statements

### 🛠️ Bug Fixes

- *(cli)* Pass entire config to process_statement

### 🚜 Refactor

- *(cli)* Use helper function to pass results back
- *(cli)* Remove hardcoded instantiation of tqdm_settings
- *(cli)* Move models to separate file

### ⚡ Performance

- *(pdf)* Make removal of vertical text optional
- *(banks)* Use transaction format if available
- Lazily import parse from dateparser

### 🧪 Testing

- *(cli)* Move files to integration directory
- *(cli)* Use tmp_path instead of cli runner isolated filesystem

### ⚙️ Miscellaneous Tasks

- *(cli)* Do not create executor if only a single file is passed
- *(cli)* Add e2e test for pprint
- *(banks/amex)* Enable safety check
- Add tests for ocr_available

## [0.17.0] - 2025-06-06

### ⛰️ Features

- *(banks)* Add amex platinum

### 🚜 Refactor

- Make multiline config transaction an optional variable
- Rename multiline_transactions -> multiline_descriptions

### ⚙️ Miscellaneous Tasks

- *(generic)* Add metadata to missing transaction message
- *(ci)* Rename regression -> performance
- Add period to date patterns

## [0.16.1] - 2025-06-04

### ⚙️ Miscellaneous Tasks

- *(ci)* Give write permission for publish workflow
- *(ci)* Don't run regression testing on main / main
- *(ci)* Add missing contents permission
- Exclude uv.lock
- *(generic)* Add metadata to missing transaction message
- *(ci)* Rename regression -> performance

### Build

- *(deps)* Bump astral-sh/setup-uv from 5 to 6

## [0.16.0] - 2025-06-01

### 🚜 Refactor

- *(ci)* Switch to ruff
- *(build)* Switch to uv

### ⚙️ Miscellaneous Tasks

- *(ci)* Test across all python versions
- *(ci)* Add regression test
- *(ci)* Remove unnecessary install of bc and jq

## [0.15.0] - 2025-05-08

### ⛰️ Features

- Add ocr support

### Build

- *(ci)* Do not cache pdftotext install
- *(deps)* Bump the deps group with 7 updates

### 📚 Documentation

- *(README)* Add instructions to install OCR extra

### Build

- *(deps)* Bump the deps group with 7 updates
- *(ci)* Do not cache pdftotext install
- *(deps)* Bump the deps group with 7 updates

## [0.14.2] - 2025-03-22

### 🛠️ Bug Fixes

- *(banks/hsbc)* Use 'Registered to:' substring match

### 📚 Documentation

- *(pyproject)* Fix incorrect license

### Build

- *(deps)* Bump the deps group with 9 updates
- *(deps)* Bump the deps group with 10 updates

## [0.14.1] - 2025-01-15

### 🚜 Refactor

- Rename suffix -> polarity

### 📚 Documentation

- *(pyproject)* Add python classifiers for 3.12 and 3.13

### ⚙️ Miscellaneous Tasks

- *(ci)* Add stale workflow
- *(pipeline/transform)* Remove redundant if clause
- *(banks)* Declare negative symbol explicitly in boa

## [0.14.0] - 2025-01-14

### ⛰️ Features

- *(banks)* Add trust

### 🛠️ Bug Fixes

- *(ci)* Pin runner to ubuntu-22.04
- *(banks/uob)* Identify
- Conditionally append statement date according to transaction

### 🚜 Refactor

- *(config)* Store multiline config in dataclass
- *(statements)* Store match data in dataclass
- *(statements)* Use OOP pattern for multiline transactions

### 📚 Documentation

- *(README)* Add Trust to supported bank list

### ⚙️ Miscellaneous Tasks

- *(generic)* Update test suite to use current year

### Build

- *(deps)* Bump the deps group with 10 updates
- *(deps)* Bump Flydiverny/setup-git-crypt from 3 to 4
- *(deps)* Bump the deps group with 12 updates

## [0.13.6] - 2024-12-13

### 🛠️ Bug Fixes

- *(banks/dbs)* Parsing transactions

## [0.13.5] - 2024-11-24

### 🚜 Refactor

- *(statements/safety)* Add additional safety check

### ⚙️ Miscellaneous Tasks

- *(banks/hsbc)* Support new statement header format

## [0.13.4] - 2024-11-15

### ⚙️ Miscellaneous Tasks

- *(banks/boa)* Disable safety check

## [0.13.3] - 2024-11-15

### 🚜 Refactor

- *(banks)* Add debit statement safety check as backup for credit statements

## [0.13.2] - 2024-11-15

### ⚙️ Miscellaneous Tasks

- *(banks/chase)* Disable safety check

## [0.13.1] - 2024-11-15

### 🛠️ Bug Fixes

- *(banks/chase)* Disable transaction auto polarity

### 🚜 Refactor

- *(banks)* Rename auto_polarity to transaction_auto_polarity

### 📚 Documentation

- *(README)* Fix bank order

## [0.13.0] - 2024-11-15

### ⛰️ Features

- *(banks)* Add support for chase credit
- *(banks)* Add bank of america combined statement

### 📚 Documentation

- *(README)* Update list of supported banks

### ⚙️ Miscellaneous Tasks

- *(banks/hsbc)* Add specific opentext version id
- *(banks/base)* Add logging for failed statement date parse

### Build

- *(deps)* Bump the deps group with 7 updates
- *(deps)* Bump the deps group with 8 updates

## [0.12.5] - 2024-09-25

### ⛰️ Features

- *(generic)* Support inconsistent header spacing across pages

### 🛠️ Bug Fixes

- *(generic)* Compile header_pattern

## [0.12.4] - 2024-09-15

### ⛰️ Features

- *(banks/dbs)* Add support for dbs-posb consolidated

### 🚜 Refactor

- *(statement/debit)* Use regex to find header on each page

### ⚙️ Miscellaneous Tasks

- Add more specific error message for missing header

## [0.12.3] - 2024-09-15

### 🛠️ Bug Fixes

- *(banks/ocbc)* Support statement date without 'TO'
- *(banks/dbs)* Use transaction_bound to exclude balances

### 🚜 Refactor

- Add ISO8601 to constants namespace
- Use ISO8601 for bank statement date patterns
- *(banks)* Shorten config variable names
- *(banks)* Declare name in bank instead of config

### ⚙️ Miscellaneous Tasks

- Remove redundant RELEASE_CHANGELOG.md
- Lower missing debit headers to debug log level

## [0.12.2] - 2024-09-08

### 🛠️ Bug Fixes

- *(banks/zkb)* Add missing apostrophe in balance regex group

### 🚜 Refactor

- Allow safety check to be disabled for specific banks

### ⚙️ Miscellaneous Tasks

- Fix typo in safety check message
- Remove redundant has_no_withdrawal_deposit_columns

## [0.12.1] - 2024-09-08

### ⛰️ Features

- *(banks)* Add support for zurcherkantonalbank

## [0.12.0] - 2024-09-08

### ⛰️ Features

- *(banks)* Add support for UOB

### 🛠️ Bug Fixes

- *(transaction)* Avoid negative zero value

### 🚜 Refactor

- *(banks)* Remove pdfconfig for stan chart and uob
- *(detector)* Simplify matching logic
- *(identifiers)* Add caching for metadata identifier
- *(detector)* Split up functions within is_bank_identified
- *(cli)* Show number of files processed/errors as final action

### ⚙️ Miscellaneous Tasks

- *(banks)* Add type check for identifiers
- *(base)* Add boundary check for transactions

## [0.11.1] - 2024-09-07

### 🚜 Refactor

- *(pdf)* Decouple unlock from PdfDocument __init__

## [0.11.0] - 2024-09-05

### ⛰️ Features

- *(banks/hsbc)* Add support for non-OCR credit statements

### 🛠️ Bug Fixes

- *(write)* Incorrect 'base' statement type in final result

### 🚜 Refactor

- *(pdf)* Make PdfDocument a child class of fitz.Document
- *(pdf)* Use file_path as first arg to PdfDocument
- *(pipeline)* Move parser & handler creation logic to extract
- Pass PdfPages instead of parser
- *(pipeline)* Move bank detection logic to CLI
- *(detector)* Move detector to banks namespace
- Remove unnecessary usage of pydantic dataclasses
- *(pdf)* Add metadata identifier attr to PdfDocument
- *(banks/base)* Fix type hint for identifiers
- *(pdf)* Lazily import ocrmypdf
- *(pdf)* Perform ocr based on metadata identifiers
- *(pipeline)* Move parser instantiation logic to CLI
- *(pipeline)* Allow custom document to be passed

### 📚 Documentation

- Remove false version from changelog
- *(README)* Add note about OCR feature

### ⚙️ Miscellaneous Tasks

- *(generic)* Add GenericParserError
- Remove unused import
- *(pdf)* Remove old get_byte_stream function
- Remove old mock_document fixture
- *(constants)* Remove case insensitive modifier from formats with no words
- *(pdf)* Improve ocrmypdf performance
- *(pipeline)* Shorten create_handler function signature
- *(generic)* Move GenericBank to generic __init__
- *(pipeline)* Import Transaction from statements namespace
- Rename generic/generic_handler to generic/handler
- Import from pymupdf instead of fitz
- Linting for ocr changes

### Build

- *(deps)* Bump the deps group with 7 updates
- *(deps)* Add ocrmypdf as a system dependency
- *(deps)* Move ocrmypdf to extras

## [0.10.10] - 2024-08-26

### 🚜 Refactor

- *(generic)* Make most common tuples into set instead of list
- *(generic)* Create separate class for pattern matching
- *(constants)* Make enums into top level file

### ⚙️ Miscellaneous Tasks

- Make CLI banner more concise
- *(generic)* Remove redundant typehint for date_regex_patterns
- *(generic)* Remove redundant results var
- *(generic)* Use self.pages directly instead of passing self.pages
- *(generic)* Rename vars/functions to use "spans" instead of tuples
- *(constants)* Move enums in config to statement

## [0.10.9] - 2024-08-21

### ⛰️ Features

- *(constants)* Add RegexEnum class to automatically compile patterns

### 🚜 Refactor

- Prevent redundant get_statement() call
- *(constants)* Add case insensitive flag directly to date groups
- *(banks)* Use single StatementConfig class
- *(banks)* Shift responsibility of regex pattern creation to config class

### 📚 Documentation

- Update PDF_PASSWORDS env var info
- Add docstring for DateFormats

### ⚙️ Miscellaneous Tasks

- Add check for missing OCR layer
- *(ci)* Disable too-few-public-methods

## [0.10.8] - 2024-08-17

### 🚜 Refactor

- *(banks)* Remove EncryptionIdentifier
- Use header patterns to identify statement type
- Use default factory instead of frozen for DateOrder
- Move PdfPasswords to pdf module
- Reduce type hint verbosity by using BaseStatement

## [0.10.7] - 2024-08-11

### 🚜 Refactor

- *(banks)* Remove encryption identifier

### ⚙️ Miscellaneous Tasks

- *(banks/sc)* Add text identifier

## [0.10.6] - 2024-08-11

### 🚜 Refactor

- Simplify bank detection function

### 📚 Documentation

- *(README)* Update information on PDF_PASSWORDS env var

### Build

- *(deps)* Bump the deps group with 7 updates

## [0.10.5] - 2024-08-03

### ⚙️ Miscellaneous Tasks

- Use simpler identifier for example bank

## [0.10.4] - 2024-08-03

### 🛠️ Bug Fixes

- *(publish)* Trigger on push of tags or manual workflow

### 🚜 Refactor

- *(handler)* Add more descriptive error for missing credit config
- *(write)* Generate hash based on transactions

## [0.10.3] - 2024-07-14

### 🛠️ Bug Fixes

- *(cd/publish)* Set release_to_pypi to true on push
- *(banks/maybank)* Add missing encryption identifier for credit statements
- *(detector)* Ensure pdf_property_identifiers are not bypassed
- *(banks)* Add identifiers for decrypted PDFs without encrypt dict

## [0.10.2] - 2024-07-14

### ⛰️ Features

- *(cli)* Add verbose output for error messages

### 🛠️ Bug Fixes

- *(pipeline)* Explicitly call get_transactions() in extract

### 🚜 Refactor

- *(statements/debit)* Recalculate debit header for each page
- *(statements/debit)* Create separate has_debit_header property
- *(statements/debit)* Remove redundant typehint for match
- Store raw_text property in PdfDocument
- *(statement)* Move regex from func to __init__
- Move identifiers to separate file
- Split up constants across multiple files
- Use RunConfig class to hold run arguments
- *(detector)* Cache metadata_items()

## [0.10.1] - 2024-07-10

### 🛠️ Bug Fixes

- Banks with only text identifiers

### 🧪 Testing

- Remove redundant `@skip_if_encrypted` from test_auto_detect_bank

### ⚙️ Miscellaneous Tasks

- *(examples)* Add text identifier example

## [0.10.0] - 2024-07-05

### 🛠️ Bug Fixes

- *(ci)* Continue even if unlock step fails
- *(ci)* Use && operator instead of &
- *(ci)* Add pdftotext deps for publish

### 🚜 Refactor

- *(statements)* Cache safety check function
- *(banks,config)* Use global password array
- *(banks)* Allow multiple sets of identifiers per bank
- *(pdf)* Split opening/unlocking logic to PdfDocument class
- *(banks/identifier)* Add more functions & remove cartesian product
- Rename MetadataAnalyzer to BankDetector

### 📚 Documentation

- *(CHANGELOG)* Only include latest changes in release

### 🧪 Testing

- Remove unused file_path var
- Add tests for pipeline with bank arg

### ⚙️ Miscellaneous Tasks

- *(statements)* Add more detailed docstring for safety check error
- *(examples)* Update single_statement with example bank arg
- *(cli)* Rename unused kwargs to _
- *(handler)* Use repr() instead of __repr__
- *(handler)* Disable broad-exeception-caught for catchall
- *(identifiers)* Use parent class for type
- *(banks/base)* Remove unnecessary if condition from validate_config
- *(constants)* Disable too-many-attrs for DateRegexPatterns

### Build

- *(deps)* Bump the deps group with 9 updates

## [0.9.5] - 2024-06-23

### ⛰️ Features

- Provide support for python 3.10

### 🛠️ Bug Fixes

- *(build)* Remove mypy from main dependencies

### 🚜 Refactor

- *(build)* Allow poetry action to skip install
- *(build)* Allow poetry action to install in system env

### 📚 Documentation

- Update old emojis in changelog
- Simplify install instructions & add dev setup
- *(README)* Add brew install alternative
- *(logo)* Support dark mode

### ⚙️ Miscellaneous Tasks

- Add brewfile dev lock file to gitignore
- Remove brewfile.dev
- Remove makefile version pin on python 3.11
- *(build)* Add runner os to poetry cache key

### Build

- *(dev-deps)* Add git cliff

## [0.9.4] - 2024-06-13

### ⛰️ Features

- *(ci)* Add publish workflow
- *(generic/constants)* Add dd_mm_yy pattern
- *(generic/constants)* Add support for dd_mm_yy pattern
- *(banks)* Add Maybank debit and credit support
- *(statements)* Attempt to calculate total sum using subtotals

### 🛠️ Bug Fixes

- *(ci)* Update step name to setup-python
- *(ci)* Run poetry tasks one at a time
- *(cli)* Allow safety_check to be passed to concurrent executor
- *(generic)* Use better default types for most_common_pattern/tuples
- *(config/typing)* Add has_withdraw_deposit_column to base statement

### 🚜 Refactor

- *(ci)* Run git-crypt unlock without temp file
- *(statement/debit)* Add better handling for suffixes
- *(metadata)* Use consistent return statement
- *(generic)* Conform to snake_case naming pattern
- *(generic/constants)* Add DRY pattern for YYYY
- *(generic/constants)* Add spaces in delimiter for all dd_mm_ patterns
- *(statements)* Remove outdated re-parsing of document with pymupdf
- *(generic/constants)* Add \b suffix for yy/yyyy patterns
- *(generic)* Add tolerance for misaligned dates across pages
- *(statement/debit)* Only try to get debit suffix if withdraw/deposit cols exist
- *(constants)* Add support for + or - in suffix
- *(banks)* Allow loose metadata field matching

### 📚 Documentation

- Add POSB to supported banks
- Add CHANGELOG using git cliff
- Move web demo gif to monopoly-streamlit
- Use emoji instead of : syntax

### 🧪 Testing

- Add newline to .gc_check file

### ⚙️ Miscellaneous Tasks

- Add CODEOWNERS file
- *(ci)* Bump poetry to 1.8.3
- Update ruff syntax
- *(ci)* Re-add flake8
- *(cli)* Add kwargs to run function
- *(generic/constants)* Change all patterns to raw string
- *(release)* Change features emoji to ⛰️
- Use 🛠️ as bug fix emoji

## [0.9.2] - 2024-06-06

### ⛰️ Features

- *(pipeline)* Support file_bytes and passwords args

### Build

- *(deps)* Support python 3.12 and pipx install

## [0.9.1] - 2024-06-05

### ⛰️ Features

- *(ci)* Add caching for `pdftotext`
- *(ci)* Add parallelism for pylint
- *(cli)* Add verbose flag

### 🚜 Refactor

- *(cli)* Use kwargs in `monopoly()`
- *(pipeline)* Improve logging
- *(ci)* Replace pylint pre-commit with ruff
- *(ci)* Use pytest -n auto precommit hook
- Use COMMA_FORMAT variable for shared amount patterns
- *(generic)* Use double curly braces instead of string template
- Shift regex compilation to base statement
- *(generic)* Use same patterns for generic and bank-specific parser
- *(generic)* Add caching for properties and transaction getter
- *(load)* Partition by statement_date
- *(pipeline)* Make `transform()` less verbose by only passing statement

### 📚 Documentation

- Update README for generic handler
- Update license badge

### 🧪 Testing

- Remove unused fixtures and args
- Use @pytest.mark.usefixtures instead of unused arg

### ⚙️ Miscellaneous Tasks

- Rename monopoly-sg to monopoly-core
- *(generic)* Add better logging in handler functions
- Add better logging for PdfParser
- Add more logging during metadata identification
- Fix type hints for identifiers
- *(brew)* Split dev dependencies into separate brewfile
- Bump to 0.9.1

### Build

- *(deps)* Bump the deps group with 5 updates

## [0.9.0] - 2024-06-02

### ⛰️ Features

- [**breaking**] Add Pipeline and GenericStatementHandler classes
- *(cli)* Allow safety check to be disabled

### 🛠️ Bug Fixes

- Standard chartered transaction pattern
- Ocbc debit statement date pattern

### 🚜 Refactor

- Remove redundant AMOUNT_WITH_CASHBACK pattern
- Make shared patterns slightly more DRY
- Create helper function to get filtered transaction lines
- Use more precise regex pattern for amounts
- Remove dbs specific logic for multiline descriptions
- Separate logic for blank line and next line check
- *(transaction)* Shorten transaction_date to transaction

### ⚙️ Miscellaneous Tasks

- Re-add python-xdist to dev deps
- Rename ExampleBankProcessor to ExampleBank
- Re-add flake8
- Bump to 0.9.0

## [0.8.2] - 2024-05-26

### 🚜 Refactor

- *(cli)* Tweak delay to 0.2
- Rename StatementFields to Columns
- Rename AccountType to EntryType
- Rename transaction_date to date on CSV

### ⚙️ Miscellaneous Tasks

- Bump to 0.8.1

## [0.8.1] - 2024-05-26

### ⛰️ Features

- *(cli)* Enable single threaded mode with -s flag

### 🚜 Refactor

- Use helper class to store date order settings
- *(cli)* Move handler import inside processing function
- Remove unnecessary pandas and numpy dependency
- *(load)* Store file formats in dictionary
- Remove unnecessary pdf2john dependency

### 🧪 Testing

- Add test for generate_name()
- Add test for cli pprint function

## [0.8.0] - 2024-05-25

### 🚜 Refactor

- *(ci)* Use git crypt action with caching
- *(processor)* Move class variables type hints to base
- Rename StatementProcessor to StatementHandler
- Move example bank to example folder
- [**breaking**] Rename processors to banks
- [**breaking**] Decouple banks from statements and parser

## [0.7.10] - 2024-05-22

### 🚜 Refactor

- Use dateparser instead of custom date patterns
- Remove dependency on bank files for generic tests
- *(config)* Default date order to DMY

### ⚙️ Miscellaneous Tasks

- Switch to AGPLv3 license
- Update gitignore

### Build

- *(deps)* Bump the deps group with 7 updates
- *(deps)* Bump tqdm from 4.66.2 to 4.66.3

## [0.7.9] - 2024-04-21

### 📚 Documentation

- Add streamlit demo

## [0.7.8] - 2024-04-21

### 🛠️ Bug Fixes

- Use correct date format for standard chartered

## [0.7.7] - 2024-04-21

### ⛰️ Features

- *(pdf)* Allow files to be passed as a byte stream

### 🚜 Refactor

- *(load)* Generate hash based on pdf metadata

### ⚙️ Miscellaneous Tasks

- Bump to 0.7.7

## [0.7.6] - 2024-04-21

### ⚙️ Miscellaneous Tasks

- Add png logo
- Add new logo

## [0.7.5] - 2024-04-20

### ⛰️ Features

- *(parser)* Raise proper exceptions during password handling
- *(parser)* Add specific exception for unsupported banks

### ⚙️ Miscellaneous Tasks

- Bump to 0.7.5

## [0.7.4] - 2024-04-19

### ⛰️ Features

- Add passwords as kwarg to detect_processor

## [0.7.3] - 2024-04-19

### 🛠️ Bug Fixes

- Date config for example bank

### Build

- *(deps-dev)* Bump idna from 3.6 to 3.7

## [0.7.2] - 2024-04-05

### 🛠️ Bug Fixes

- *(processor)* Handle leap year dates

### ⚙️ Miscellaneous Tasks

- Update black formatting

### Build

- *(deps)* Bump the deps group with 7 updates
- *(deps)* Bump the deps group with 5 updates

## [0.7.1] - 2024-02-11

### 🛠️ Bug Fixes

- *(processor)* Improve handling for multi-year statements

### Build

- *(deps)* Bump the deps group with 6 updates
- *(deps-dev)* Bump cryptography from 41.0.6 to 42.0.0

## [0.7.0] - 2024-02-07

### 🚜 Refactor

- *(statements)* Raise exception if safety check fails

## [0.6.7] - 2024-02-07

### ⛰️ Features

- *(statements/credit)* Support multiple prev balances

### 🛠️ Bug Fixes

- *(statements/debit)* Ralign header pos instead of lalign

### 🚜 Refactor

- *(cli)* Broaden error catching

### 📚 Documentation

- Note for dbs debit statement

## [0.6.6] - 2024-01-12

### ⛰️ Features

- *(cli)* Add --version flag
- Add support for cloud run secrets via env var

### 🚜 Refactor

- *(tests/cli)* Add cli_runner flag
- *(config)* Use secret string to obscure passwords

### ⚙️ Miscellaneous Tasks

- Bump to 0.6.6

## [0.6.5] - 2024-01-07

### 🚜 Refactor

- *(statement)* Use re.search to catch hsbc second date

## [0.6.4] - 2024-01-07

### 🛠️ Bug Fixes

- Handling for cross-year transactions

### Build

- *(deps)* Bump the deps group with 9 updates

## [0.6.3] - 2024-01-03

### 🛠️ Bug Fixes

- *(dbs)* Statements may sometimes have transactions on the last page
- *(pdf)* Attempt to proceed without garbage collection on first pass

## [0.6.2] - 2024-01-02

### ⛰️ Features

- *(statements/base)* Include statement name in safety warning message

### 🛠️ Bug Fixes

- *(statements/debit)* Mitigate error caused by False == False -> True logic
- *(ocbc)* Only use one method to get text from pdf
- *(ocbc)* Remove redundant page filter

### 🚜 Refactor

- *(tests)* Create DRY fixture for statement setup

### ⚙️ Miscellaneous Tasks

- Bump to 0.6.2

## [0.6.1] - 2023-12-29

### 🛠️ Bug Fixes

- *(write)* Use variable instead of string

## [0.6.0] - 2023-12-28

### 🛠️ Bug Fixes

- Regex pattern for example statement

### 🚜 Refactor

- Use separate config class for debit and credit
- Create separate processing for debit and credit
- Always run safety check
- *(statement)* Split safety check logic for debit & credit
- *(processor)* Split debit and credit statement processing
- *(statement)* Allow debit_config to be undeclared in bank processor subclasses
- *(base-processor)* Remove redundant class attributes
- *(processor-base)* Migrate statement creation logic to base
- *(statements)* Group statement classes within directory + create base class
- *(statements)* Rename debit_account_identifier to debit_statement_identifier

### 📚 Documentation

- *(README)* Remove reference to apt
- *(processor)* Add function docstrings

### ⚙️ Miscellaneous Tasks

- Update example statement
- Bump to 0.6.0

## [0.5.0] - 2023-12-05

### ⛰️ Features

- Add support for debit statements

### 🚜 Refactor

- *(processor)* Remove redundant else condition from convert_date
- *(statement)* Reduce property nesting for statement_date
- *(statement)* Let processor handle injection of prev mth balance

### Build

- Add grouping for dependabot PRs
- *(deps)* Bump tqdm from 4.65.0 to 4.66.1
- *(deps)* Bump pymupdf from 1.23.6 to 1.23.7
- Bump dependencies
- *(deps-dev)* Bump the deps group with 2 updates

## [0.4.7] - 2023-12-02

### 🚜 Refactor

- *(load)* Hash using raw pdf content instead of filename

## [0.4.6] - 2023-12-01

### 🚜 Refactor

- *(processor)* Allow file path to be passed as string or Path

## [0.4.5] - 2023-11-30

### Build

- Switch from using apt to brew for poppler

## [0.4.4] - 2023-11-30

### 🚜 Refactor

- Rename bank -> processor

### 📚 Documentation

- *(README)* Add gif

### ⚙️ Miscellaneous Tasks

- *(cli)* Reword command for clarity

### Build

- *(deps)* Bump cryptography from 41.0.5 to 41.0.6

## [0.4.3] - 2023-11-27

### ⛰️ Features

- *(cli)* Add error handling
- *(cli)* Add option to print df repr of statement

### 🚜 Refactor

- *(cli)* Processed_statement -> target_file_name

### 📚 Documentation

- *(cli)* Improve docstrings for modules & classes

### ⚙️ Miscellaneous Tasks

- Bump monopoly to 0.4.3

## [0.4.2] - 2023-11-27

### ⛰️ Features

- *(processor)* Add unique ids for output files

## [0.4.1] - 2023-11-26

### ⛰️ Features

- *(cli)* Add concurrency

## [0.4.0] - 2023-11-26

### ⛰️ Features

- *(ci)* Add dependabot
- *(cli)* Allow custom output directory
- Add file to check git crypt status
- *(tests)* Skip tests if git crypt is locked
- *(cli)* Add welcome message
- *(cli)* Add progress bar

### 🛠️ Bug Fixes

- *(README)* Badges
- Re-add example statement via gitignore

### 🚜 Refactor

- Move output dir to same level as statement dir
- Move write csv logic into load function
- Return all identifiers instead of only the first
- Move example bank to banks dir
- [**breaking**] Drop support for john

### 📚 Documentation

- *(README)* Update

### ⚙️ Miscellaneous Tasks

- Bump monopoly to 0.4.0

### Build

- *(deps)* Bump urllib3 from 1.26.16 to 1.26.18
- *(deps)* Bump actions/checkout from 3 to 4 (#52)
- *(deps-dev)* Bump pylint from 2.17.5 to 3.0.2 (#53)
- *(deps)* Bump pymupdf from 1.23.3 to 1.23.6 (#54)
- *(deps-dev)* Bump taskipy from 1.12.0 to 1.12.2 (#55)
- *(deps-dev)* Bump pytest from 7.4.1 to 7.4.3 (#56)
- *(deps)* Bump pydantic-settings from 2.0.3 to 2.1.0 (#57)

## [0.3.0] - 2023-11-23

### ⛰️ Features

- Add barebones cli
- *(statement)* Add previous statement balance as transaction

### 🛠️ Bug Fixes

- Move output to src directory
- *(README)* Point badges at main workflow
- *(build)* Modify poetry shell to use python 3.11
- *(banks/hsbc)* Read all pages

### 🚜 Refactor

- *(banks/base)* Reduce error verbosity
- *(processor)* Rename csv to write to avoid name conflict
- Create src directory to hold monopoly
- *(ci)* Switch from docker to local gha runner tests
- Install pdftotext dependencies with apt
- *(statement)* Turn _process_line into class method
- *(statement)* Shorten statement config class variables
- *(statement)* Treat credit card transactions as debit entry

### 📚 Documentation

- *(README)* Fix installation order

### Build

- Pin python to 3.11.x

## [0.2.0] - 2023-11-05

### ⛰️ Features

- *(tests)* Add test for statement line lstrip
- *(banks/hsbc)* Allow use of hsbc_pdf_password instead of only hsbc_pdf_password_prefix
- *(tests)* Add test to check that Transaction and StatementFields use equivalent names
- *(banks)* Add automatic bank detection
- *(banks)* Add safety check for transactions
- *(banks)* Add cashback support for ocbc and citibank
- *(tests)* Add test for example bank

### 🛠️ Bug Fixes

- *(ci)* Update local hook to use task for test

### 🚜 Refactor

- *(constants/enums)* DRY shared transaction patterns
- *(pdf)* Raise error if document is still encrypted at end of open()
- *(pdf)* Allow access to pdf document + encrypt dict via cached properties
- *(tests/banks)* Differentiate expected vs current results
- *(log)* Reduce verbosity
- Rename storage to csv & move to root dir
- *(processor)* Reduce number of transformation functions
- *(processor)* Shorten safety check function
- *(statement)* Remove redundant arbitrary_config
- [**breaking**] Reduce number of attributes in statement config

### 📚 Documentation

- *(README)* Remove old cloud implementation picture
- Add class (and some module) level docstrings
- *(config)* Add docstring for transactionconfig
- *(README)* Update features

### Build

- Bump pdf2john to 0.1.5

## [0.1.2] - 2023-10-30

### 📚 Documentation

- *(README)* Add more specific project description
- *(README)* Use raw image for readme

## [0.1.1] - 2023-10-30

### ⛰️ Features

- Update poetry dependencies
- Add boilerplate code
- Add terraform boilerplate code
- *(ocbc)* Add test for 365
- Add constants to improve readability
- *(ci)* Add linting and formatting
- *(ci)* Add pre-commit hook
- Add tests for opening files
- *(tf)* Add bucket for processed files
- *(ocbc)* Add date transform with dec/jan handling
- *(pdf)* Convert amount to float
- Add helper function for GCS
- *(pdf)* Add load function + write to disk
- Add dockerfile
- *(tf)* Enable APIs via IaC
- *(tf)* Add artifact registry repository
- *(ci)* Add Makefile for docker build/push commands
- *(tf)* Add pubsub topic and give access to gmail
- *(ci)* Add docker compose yaml
- Create secret for gmail token
- Bump python & poetry versions
- *(tf)* Give service account access to secret
- Add function to set up gmail push notifications
- Default docker entrypoint as gmail pubsub
- *(ci)* Add pylint
- *(gmail)* Add extract pdf functions
- Create entrypoint for cloud run function
- Add logging
- Give bucket permissions to svc account
- *(tf)* Create iac for cloud run function
- *(main)* Add support for multiple emails with attachments
- *(tf)* Add cloud scheduler job iac, trigger to run every hour
- *(pdf)* Add support for page range selection
- *(pdf)* Allow pages to be cropped
- *(banks)* Add support for hsbc statement
- *(hsbc)* Add support for transformations
- Add hsbc to main entrypoint
- *(pdf)* Use helper class to store processed data instead of returning string
- *(gmail)* Add support for nested parts
- *(banks)* Raise error if extract doesn't have transactions
- *(banks)* Raise error if extract doesn't return statement date
- *(banks)* Add citibank credit class (#1)
- *(banks)* Simplify transaction date parsing
- *(gcp)* Add uuid to blob names
- *(pdf)* Use JtR to automatically unlock PDFs
- *(ocbc)* Add page bbox for pdf statement
- *(banks)* Output csv location in logs
- Add examples
- *(citibank)* Add password support
- *(hsbc)* Allow password to override masking
- *(tf)* Add bigquery dataset and table
- *(banks)* Allow for manual password override
- *(banks)* Allow override from top of class
- *(pdf)* Set page segementation mode as pdfconfig var
- *(banks)* Add support for standard chartered
- *(ci)* Update workflow to install pdftotext
- *(banks)* Add support for dbs
- *(pdf)* Raise error if document is null after opening
- *(ci)* Add mypy to workflow

### 🛠️ Bug Fixes

- *(ocbc)* Password logic
- *(ocbc)* Remove whitespaces from description
- *(ocbc)* Support statements outside of cross-year logic
- *(pdf)* Pass file path to upload function
- Client cannot be pickled, must be explicitly called
- *(tesseract)* Set page segmentation mode to 4 (single col of text)
- *(tf)* Add missing hsbc password var
- Use same filename for cloud and local
- Only mark processed emails as read
- *(gmail)* Pass list instead of email object
- *(gmail)* Prevent redundant creation of client & make it mockable
- *(banks)* Handle comma in amount string & get lines from object
- *(gmail)* Error should be raised if no attachment
- *(main)* Switch to re.search instead of match
- *(README)* Update test workflow yaml
- *(banks)* Allow pdf config to be optional
- *(statement)* Coerce amount with comma to float
- *(pydantic)* Update validator and types to avoid deprecationwarning
- *(ci)* Reduce pytest warning noise for grpc deprecation warning
- Update example bank enum and column name

### 🚜 Refactor

- [**breaking**] Boilerplate code for ocbc365
- Update project dependencies
- Get filename attr, drop redundant attr
- Decouple text extraction from df creation
- Use enums instead of strings for columns
- Columns to lowercase
- Create separate method for opening files
- *(pdf)* Extract raw text and transactions separately
- *(pdf)* Import DataFrame directly
- *(ocbc)* Return raw date string instead of object
- *(pdf)* Allow instantiation without file path
- *(pdf)* Change transform to static method
- Use pydantic for env var management
- *(ci)* Set max line length to 88
- Follow liskov substitution principle
- Remove nested conditions from _transform_date function
- *(pdf)* Move generate_blob_name to helper function
- *(pdf)* Move generate_file_name to helper file
- *(pdf)* Use one function to generate file/blob names
- *(pdf)* Create statement data class to hold non-PDF variables
- Remove redundant else condition
- *(gmail)* Move credential functions to separate file
- Use fitz instead of pdf2image
- Remove redundant dependencies
- Create attachment class and group related functions
- *(gmail)* Pass in trusted user list as env var
- Rename persist_attachment_to_disk -> save
- *(tf)* Paramterize project and region variables
- *(pdf)* Change _open_pdf to public static method
- *(pdf)* Split process page logic to separate function
- *(pdf)* Revert page deletion logic
- *(gmail)* [**breaking**] Move attachment and email logic to gmail class
- *(gmail)* Do not fail if no emails found
- *(pdf)* Move transformation to ocbc class
- *(pdf)* Move load to ocbc class
- *(gmail)* Exit(0) if no unread emails
- *(statement)* Move date conversion function to child class
- *(banks/dataclasses)* Break monolithic banks class into subclasses
- *(dataclasses/statement)* Pass in statement args dynamically
- *(statement)* Add transactions and statement_date as class properties
- *(banks)* Set statement config as class level constant
- *(banks)* DRY cross-year date transformation logic
- *(banks)* Move logging to parent _transform_date_to_iso
- *(banks)* [**breaking**] Decouple pages from statement class, pages are now passed as an arg
- *(banks)* Simplify and DRY config inheritance logic
- *(main)* Abstract statement date/df logic out of main function
- *(main)* Move processing logic to separate function
- *(main)* Move gmail client instantiation out of function definition
- *(gmail)* Move nested classes out of message class for better readability
- *(pdf)* Allow password to be nullable
- *(pdf)* Allow parser to have null config
- *(pdf)* Filter out empty lines from pdf
- *(pdf)* Switch to re.findall for multiline patterns
- Make bank classes generic by removing card-specific values
- Reduce directory and file nesting
- Make settings optional
- *(tf)* Move project id, region and secret name to variables
- *(banks)* Use enums for account type and bank name
- *(banks)* Use statement enum class instead of specific enums
- *(statement)* Simplify transactions property
- *(banks)* Allow custom csv path for load function
- *(statement)* Use transaction class to encapsulate statement enums
- *(terraform)* Rename hsbc_password var to hsbc_password_prefix
- *(citibank)* Add page bbox and only match from string start
- *(banks,statement)* Use pydantic dataclasses
- *(statement)* Use re.search instead of re.findall
- *(statement)* Unpack regex match into transaction class
- *(statement)* Use if condition instead of try expect to avoid IndexError
- *(statement)* Add validation for regex date format patterns
- *(statement)* Rename date_pattern to statement_date_pattern
- *(tests)* Separate tests into unit and integration
- *(examples)* Use fictional bank example
- *(banks)* Make bank submodules available at directory level
- *(log)* Move logger definition logic out of __init__
- Move constants out of helper directory to root dir
- Move statement & pdf config to config file
- *(banks)* Move banks to subdirectories
- *(banks)* Move upload and csv functions to separate file
- Rename bankstatement enum to statementfields
- [**breaking**] Rename bank to statementprocessor
- *(banks)* Use enums for transaction pattern
- *(banks)* Move generate_name function to storage file
- *(pdf)* Import PdfHashExtractor from pdf2john 0.1.2
- *(examples)* Move helper bank class to separate file
- *(ci)* Only run time consuming tests on PR
- *(banks)* Revert to having extract() handle pages
- *(banks)* Always transform dates
- *(banks)* Add pdf parser to init
- *(statement)* Rename date to transaction date
- *(banks)* Add pdf parser to init
- *(pdf)* Create separate class for brute force configuration
- *(banks)* Use \s+ instead of s\*
- *(tests)* Remove redundant test to avoid concurrency conflict
- [**breaking**] Switch from pytesseract to pdftotext
- *(pdf)* Lstrip lines to allow for more specific regex patterns
- *(pdf)* Remove redundant argument to remove vertical text
- *(banks/hsbc)* Use simpler regex for ddescription
- *(banks)* Use more specific regex patterns
- *(constants)* Use auto() instead of hardcoding enum values
- *(constants)* DRY transaction patterns
- *(constants)* Get transaction patterns to follow alphabetical order
- *(tests)* Create generic test for date handling
- *(tests)* Create generic test for csv loading
- *(tests)* Run tests on extract/transform for each bank
- *(tests)* Create single extract/transform tests for all banks
- *(tests)* Move bank PDF fixtures to same dir as test files
- *(banks)* Make pdf config optional
- [**breaking**] Remove cloud code from monopoly
- *(ci)* Remove pytest xdist

### 📚 Documentation

- *(README)* Add better install + usage instructions
- *(README)* Add logo
- *(README)* Add black and mit license badges
- *(README)* Add instructions on handling encrypted pdfs
- *(README)* Add tests badge
- *(README)* Add pylint badge
- *(README)* Add ci passing badge
- *(README)* Rename redundant monopoly header
- *(pyproject)* Add README.md

### 🧪 Testing

- *(ocbc)* Switch to assert_frame_equal
- *(ocbc)* Switch to integration test
- *(ocbc/transform)* Add test case for data within year
- *(ocbc)* Pass date directly instead of strptime
- Speed up with xdist
- *(ocbc/load)* Remove redundant check_dtype bool
- *(pdf,ocbc)* Add fixture to re-use class instances
- *(ocbc)* Use ocbc statement date var
- Speed up by using dummy gmail service
- Check total sum of raw df
- Move fixtures to common folder
- Add tests for statement date extraction
- Revert to single fixture per bank instance
- Remove unused fixture
- Use fixture to avoid accidentally calling gmail client
- Add test for main gmail entrypoint
- Add fixtures for citibank, hsbc, ocbc (#2)
- Use statement enum class for date, description, amount
- Add test for statement line processing

### ⚙️ Miscellaneous Tasks

- Update git ignore
- Update deps
- Create LICENSE.md
- Rename merchant details -> description
- *(ci)* Set black max length to 79
- *(ocbc)* Remove date transform pseudocode
- *(ocbc)* Rename test and variables to be more specific
- Split format, lint and test into separate steps
- Update pyproject config
- Add .gitkeep to output folder
- Set message retention on topic to 1 day
- Create default action for makefile
- Linting
- Update precommit hooks
- Enable upload_to_cloud bool
- *(tf)* Simplify name for service account
- Remove incorrect type hints
- *(pdf)* Add better logging for page processing
- *(pdf)* Fix type hint for get_pages
- Run pytest-xdist
- Add github ci workflow
- Add pdf example
- *(tf)* Formatting
- *(bank)* Remove obsolete date_parser attribute
- Rename test.yaml workflow to tests.yaml
- Add flake8 pre-commit hook
- Remove redundant example enum

### Build

- Update to python 3.11
- Set entrypoint to main
- Update all packages & bump pandas to 2.1.0
- *(ci)* Share cache for builds across branches
- *(ci)* Update to setup buildx v3 and remove QEMU support
- Add dist to gitignore
- Remove redundant main entrypoint

## [0.1.0] - 2023-09-09

### ⛰️ Features

- Initial commit
- Gitignore
- Add dependencies

<!-- generated by git-cliff -->
