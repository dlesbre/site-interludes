# Change Log

## Version ??? - soon

- Changed planning break from midnight to 4am
- Make slot start field non-nullable to simplify code

## Version 1.2.1 - 2021-04-24

- Fix too small character limit on activity description
- Added links to more games
- Fix typos
- Added colors to planning
- Added caption to planning, can be set in site_settings

## Version 1.2.0 - 2021-04-07

- Update inscription form and displayed info for 'at home' event.
- Update metrics to remove unused info (meals, sleeps, ...)
- Added link to discord
- Changed models for repeated activities to a separate "slot" table (cleaner)
- Added check for slotless activity before sending mails
- Added HTML formatting for global message

## Version 1.1.0 - Repeated Activities - 2021-03-30

- Fix typos, wrong value displays
- Reworked activity display and allow HTML display inputs
- Allowed easy activity duplication
- Separate activity must_subscribe display from actual subscriptions
	(so a single activity can have multiple clones: one displayed in list, and multiple in
	planning and inscription lists if occurs more than once)
- Added links to activities from profile page
- Added admin warning for malformed activity wishes.
- Fixed multiple day display on planning and added planning preview to admin files
- Added version number to admin pages

## Version 1.0.1 - day one patch - 2021-03-24

- Fix missing field `is_staff` in user model
- Fix non-nullable setting `activity_submission_form`

## Version 1.0.0 - 2021-03-24

- Initial release
