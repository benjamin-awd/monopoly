# Changelog

All notable changes to this project will be documented in this file.

## [0.9.1] - 2024-06-09

### 🚀 Features

- *(pipeline)* Support file_bytes and passwords args

### Build

- *(deps)* Support python 3.12 and pipx install

## [0.9.0] - 2024-06-09

### 🚀 Features

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

## [0.8.2] - 2024-06-09

### 🚀 Features

- [**breaking**] Add Pipeline and GenericStatementHandler classes
- *(cli)* Allow safety check to be disabled

### 🐛 Bug Fixes

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

## [0.8.1] - 2024-06-09

### 🚜 Refactor

- *(cli)* Tweak delay to 0.2
- Rename StatementFields to Columns
- Rename AccountType to EntryType
- Rename transaction_date to date on CSV

### ⚙️ Miscellaneous Tasks

- Bump to 0.8.1

## [0.8.0] - 2024-06-09

### 🚀 Features

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

## [0.7.10] - 2024-06-09

### 🚜 Refactor

- *(ci)* Use git crypt action with caching
- *(processor)* Move class variables type hints to base
- Rename StatementProcessor to StatementHandler
- Move example bank to example folder
- [**breaking**] Rename processors to banks
- [**breaking**] Decouple banks from statements and parser

## [0.7.9] - 2024-06-09

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

## [0.7.8] - 2024-06-09

### 📚 Documentation

- Add streamlit demo

## [0.7.7] - 2024-06-09

### 🐛 Bug Fixes

- Use correct date format for standard chartered

## [0.7.6] - 2024-06-09

### 🚀 Features

- *(pdf)* Allow files to be passed as a byte stream

### 🚜 Refactor

- *(load)* Generate hash based on pdf metadata

### ⚙️ Miscellaneous Tasks

- Bump to 0.7.7

## [0.7.5] - 2024-06-09

### ⚙️ Miscellaneous Tasks

- Add png logo
- Add new logo

## [0.7.4] - 2024-06-09

### 🚀 Features

- *(parser)* Raise proper exceptions during password handling
- *(parser)* Add specific exception for unsupported banks

### ⚙️ Miscellaneous Tasks

- Bump to 0.7.5

## [0.7.3] - 2024-06-09

### 🚀 Features

- Add passwords as kwarg to detect_processor

## [0.7.2] - 2024-06-09

### 🐛 Bug Fixes

- Date config for example bank

### Build

- *(deps-dev)* Bump idna from 3.6 to 3.7

## [0.7.1] - 2024-06-09

### 🐛 Bug Fixes

- *(processor)* Handle leap year dates

### ⚙️ Miscellaneous Tasks

- Update black formatting

### Build

- *(deps)* Bump the deps group with 7 updates
- *(deps)* Bump the deps group with 5 updates

## [0.7.0] - 2024-06-09

### 🐛 Bug Fixes

- *(processor)* Improve handling for multi-year statements

### Build

- *(deps)* Bump the deps group with 6 updates
- *(deps-dev)* Bump cryptography from 41.0.6 to 42.0.0

## [0.6.7] - 2024-06-09

### 🚜 Refactor

- *(statements)* Raise exception if safety check fails

## [0.6.6] - 2024-06-09

### 🚀 Features

- *(statements/credit)* Support multiple prev balances

### 🐛 Bug Fixes

- *(statements/debit)* Ralign header pos instead of lalign

### 🚜 Refactor

- *(cli)* Broaden error catching

### 📚 Documentation

- Note for dbs debit statement

## [0.6.5] - 2024-06-09

### 🚀 Features

- *(cli)* Add --version flag
- Add support for cloud run secrets via env var

### 🚜 Refactor

- *(tests/cli)* Add cli_runner flag
- *(config)* Use secret string to obscure passwords

### ⚙️ Miscellaneous Tasks

- Bump to 0.6.6

## [0.6.4] - 2024-06-09

### 🚜 Refactor

- *(statement)* Use re.search to catch hsbc second date

## [0.6.3] - 2024-06-09

### 🐛 Bug Fixes

- Handling for cross-year transactions

### Build

- *(deps)* Bump the deps group with 9 updates

## [0.6.2] - 2024-06-09

### 🐛 Bug Fixes

- *(dbs)* Statements may sometimes have transactions on the last page
- *(pdf)* Attempt to proceed without garbage collection on first pass

## [0.6.1] - 2024-06-09

### 🚀 Features

- *(statements/base)* Include statement name in safety warning message

### 🐛 Bug Fixes

- *(statements/debit)* Mitigate error caused by False == False -> True logic
- *(ocbc)* Only use one method to get text from pdf
- *(ocbc)* Remove redundant page filter

### 🚜 Refactor

- *(tests)* Create DRY fixture for statement setup

### ⚙️ Miscellaneous Tasks

- Bump to 0.6.2

## [0.6.0] - 2024-06-09

### 🐛 Bug Fixes

- *(write)* Use variable instead of string

## [0.5.0] - 2024-06-09

### 🐛 Bug Fixes

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

## [0.4.7] - 2024-06-09

### 🚀 Features

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

## [0.4.6] - 2024-06-09

### 🚜 Refactor

- *(load)* Hash using raw pdf content instead of filename

## [0.4.5] - 2024-06-09

### 🚜 Refactor

- *(processor)* Allow file path to be passed as string or Path

## [0.4.4] - 2024-06-09

### Build

- Switch from using apt to brew for poppler

## [0.4.3] - 2024-06-09

### 🚜 Refactor

- Rename bank -> processor

### 📚 Documentation

- *(README)* Add gif

### ⚙️ Miscellaneous Tasks

- *(cli)* Reword command for clarity

### Build

- *(deps)* Bump cryptography from 41.0.5 to 41.0.6

## [0.4.2] - 2024-06-09

### 🚀 Features

- *(cli)* Add error handling
- *(cli)* Add option to print df repr of statement

### 🚜 Refactor

- *(cli)* Processed_statement -> target_file_name

### 📚 Documentation

- *(cli)* Improve docstrings for modules & classes

### ⚙️ Miscellaneous Tasks

- Bump monopoly to 0.4.3

## [0.4.1] - 2024-06-09

### 🚀 Features

- *(processor)* Add unique ids for output files

## [0.4.0] - 2024-06-09

### 🚀 Features

- *(cli)* Add concurrency

## [0.3.0] - 2024-06-09

### 🚀 Features

- *(ci)* Add dependabot
- *(cli)* Allow custom output directory
- Add file to check git crypt status
- *(tests)* Skip tests if git crypt is locked
- *(cli)* Add welcome message
- *(cli)* Add progress bar

### 🐛 Bug Fixes

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

## [0.2.0] - 2024-06-09

### 🚀 Features

- Add barebones cli
- *(statement)* Add previous statement balance as transaction

### 🐛 Bug Fixes

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

## [0.1.2] - 2024-06-09

### 🚀 Features

- *(tests)* Add test for statement line lstrip
- *(banks/hsbc)* Allow use of hsbc_pdf_password instead of only hsbc_pdf_password_prefix
- *(tests)* Add test to check that Transaction and StatementFields use equivalent names
- *(banks)* Add automatic bank detection
- *(banks)* Add safety check for transactions
- *(banks)* Add cashback support for ocbc and citibank
- *(tests)* Add test for example bank

### 🐛 Bug Fixes

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

## [0.1.1] - 2024-06-09

### 📚 Documentation

- *(README)* Add more specific project description
- *(README)* Use raw image for readme

## [0.1.0] - 2024-06-09

### 🚀 Features

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

### 🐛 Bug Fixes

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
