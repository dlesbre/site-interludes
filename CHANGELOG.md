<!-- LTeX: language=en -->

# Change Log

## master

- Add uploadable file for logo and favicon
- Made the hosting school an enum with dynamic how-to-get-here and footer sponsor
- Made prices into settings, no longer hardcoded, added totals to metrics
- Added the "Guide de l'administrateur" page with useful info
- Add a disclaimer for personnal data handling
- Added the legal mentions page
- Made meal menus into settings
- Improve date display when event is on a month-split weekend
- Add a check for undisplayed activities
- Add a disclaimer for undisplayed activites shown in the planning
- Send an email to admins on new activity submission
- Add a check that slot and activity registration matches
- Communicate murder XP to DMs
- Per school email
- Per school participant export
- Send only one email par orga
- Send email communicating time slots

## Version 3.0.0 - 2022-12-02 - Interludes 2023 Saclay

- Merge saclay's fork
- Add a salaried/unsalaried field to separate prices
- Add a nb_murder fields to have info on personal experience with murders
- Add a comment field for participant to indicate extra data
- Separate activity inscription open from inscription open settings

## Version 2.2.0 - 2022-09-10 - Changes from 48h des jeux

- Merge Lyon's fork
- Added dynamic (in DB) templates for info pages (home and faq)
- Restore meals to inscription form (as they can be easily removed if irrelevent)
- Spelling fixes

## Version 2.1.0 - 2022-03-24 - Interludes 2022 Lyon

- Update website for Lyon 2022
- Made hosting school a parameter
- Added distinction between this website and the HelloAsso ticket website

## Version 2.0.0 - 2021-10-05 - Changes from 48h des jeux website

- Added a form that allows admins to send emails to all users
- Added a form for users to submit activities
- Added a changeable caption for the planning
- Added fixes/improvement from 48h des jeux:
	- bug fixed in activity submission form
	- new validator that checks the number of slots for each activity in the planning
	- fixed room display on activity page
	- fixed planning info displayed on activity even when planning hidden
	- added boolean field to show host email on activity
	- added boolean field to separate showing slot on planning and next to activity

## Version 1.2.8 - 2021-05-06 - Interludes 2021 Ulm

- Added links to FAQ
- Added django-admin link to admin profile page

## Version 1.2.7 - 2021-05-03

- Fix broken discord link

## Version 1.2.6 - 2021-05-03

- Added CSS version number query string to force reload on display breaking changes
- Added more links to discord server
- Mentionned that subscriptions are optionnal

## Version 1.2.5 - 2021-04-30

- Added logo !
- Added check for inscription to multiple instances of same activity
- Fixed planning bugs
- Added missing columns to some CSV exports
- Added optionnal nullable field to change a slot's duration

## Version 1.2.4 - 2021-04-28

- Custom title to error pages
- Update FAQ
- More captions for planning
- Reworked file upload to allow for file replacement (and not just upload to a new unique name)
- Fix bugs
- Added links to home page

## Version 1.2.3 - 2021-04-25

- Planning bug fixes

## Version 1.2.2 - 2021-04-25

- Changed planning break from midnight to 4am-8am
- Added "back to top" links to activity pages
- Make slot start field non-nullable to simplify code
- Added planning caption
- Added planning PDF upload and download

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
