# adjustapi


Don't forget to initialize database:

flask init-db

This command will convert the csv dataset to a relational database.

Example of url paths for common api use-cases:
 
 1. /api/getdata?show=channel+country+impressions+clicks&group=channel+country&sort=clicks-&tdate=<=2017-06-01
 2. /api/getdata?show=tdate+os+installs&group=tdate&sort=tdate&tdate=2017-05-31_2017-05-01
 3. /api/getdata?show=tdate+os+revenue&tdate=2017-06-01&country=US&group=os&sort=-revenue
 4. /api/getdata?show=spend&cpi=true&country=CA&group=channel&sort=cpi-
