# Contributing to Open Creator

Thank you for your interest in contributing to Open Creator! As an open-source project, we value your input and collaboration in our quest to empower individuals with customizable skill libraries.

There are numerous avenues to contribute, ranging from bug reporting and feature suggestions to direct code enhancements. Your efforts in enriching this project are deeply appreciated.

## Roadmap

We're currently in the process of crafting a public roadmap that will provide insight into our priorities and forthcoming improvements.

Presently, our primary focus revolves around addressing issues related to the integration of various tools and maintaining the core logic of the creator. Our mission is to make coding skills readily available, even to those with limited coding backgrounds.

In light of this, our aspiration is to maintain a straightforward codebase rather than an overly intricate one. We are driven by the vision of transforming words into actionable skills, even for non-coders. We eagerly welcome dialogues on preserving this approach as we introduce new features.

## Reporting Issues

Should you stumble upon a bug or conceive a potentially beneficial feature, please don't hesitate to [open a new issue](https://github.com/timedomain-tech/open-creator/issues/new/choose). For a prompt and efficient response, kindly provide:

- **Bug Reports:** Detailed steps to recreate the issue, specifics about your OS, Python version, and, if necessary, relevant screenshots and code/error snippets.
- **Feature Requests:** A thorough description of how your suggestion could enhance Open Creator and its community.

## Contributing Code

Code contributions via pull requests are highly encouraged. Here are some guidelines to ensure a smooth process:

- For significant code alterations, we recommend discussing your ideas on [Discord] first to ensure alignment with our project's ethos. Our objective is to keep the codebase accessible and uncomplicated for newcomers.

- Fork the repository and branch out for your modifications.

- Ensure your changes are accompanied by clear code comments that elucidate your strategy. Aim to adhere to the code's existing conventions.

- Initiate a PR to `main`, linking any associated issues. Furnish comprehensive details about your amendments.

- We'll review PRs as promptly as feasible and collaborate with you on integration. Kindly be patient, as reviews can be time-intensive.

- Upon approval, your contributions will be merged. A huge thank you for elevating Open Creator!

## Running Your Local Fork

After forking and branching, follow these steps to run your local fork:

1. Navigate to the project directory `/open-creator`.
2. Install dependencies with `poetry install`.
3. Execute the program via `poetry run creator`.

Post-modifications, re-run with `poetry run creator`.

### Installing New Packages

For new dependency additions, utilize `poetry add package-name`.

### Known Issues

If `poetry install` seems to freeze on certain dependencies, attempt:

```shell
export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring
```

Then, re-run `poetry install`. If issues persist, our [Discord community][discord] is always available for assistance.

## Questions or Doubts?

Our [Discord community][discord] is a vibrant space for connecting with fellow contributors. We're more than happy to assist you on your maiden open-source contribution journey!

## Licensing

All contributions to Open Creator are governed by the MIT license.

Your patience and understanding as we refine our operations are invaluable. Thank you for being an integral part of our community!

[discord]: https://discord.gg/mMszyg2j

