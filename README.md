(much of this is now old. Ask if you have questions)

## Security policies

### General access

Three levels:
- **technology** - access to all technology assets, such as the sixty & infrastructure repos
- **investment** - access to all proprietary investment assets apart from investment strategies
- **administrator** - access to everything, including changing permissions. Includes investment strategies by default


### Strategy access

Access to investment strategies (sector / commodity) is on a strategy-by-strategy basis.

Each has a group on AWS, which people are added individually to the repos on GitHub

### Circle-CI access

There is a Circle-CI user for each level required:
- circle-technology
- circle-investment
- circle-strategy-*

These need to be added to the relevant Circle-CI project's environment variable
