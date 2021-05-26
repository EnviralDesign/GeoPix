import patreon
import os
import time

access_token = os.environ.get('PATREON_ACCESS_TOKEN')

api_client = patreon.API(access_token)
campaign_response = api_client.fetch_campaign()

# only need to fetch campaign id dynamically once, and hard code. it won't change.
# campaign_id = campaign_response.data()[0].id()
campaign_id = 4953171

print('Fetching Patron Info...')
all_pledges = []
cursor = None
page = 0
while True:
	print('Fetching Page %i...'%(page))
	pledges_response = api_client.fetch_page_of_pledges(
		campaign_id , 25 , 
		cursor=cursor,
		fields = {'pledge': ['total_historical_amount_cents', 'declined_since', ]}
	)
	cursor = api_client.extract_cursor( pledges_response )
	all_pledges += pledges_response.data()
	if not cursor:
		break

pledges_info = []

for pledge in all_pledges:
	declined = pledge.attribute('declined_since')
	reward_tier = 0

	if pledge.relationships()['reward']['data']:
		reward_tier = pledge.relationship('reward').attribute('amount_cents')

	if not declined:
		pledges_info.append({
			'full_name': pledge.relationship('patron').attribute('full_name'),
			'total_historical_amount_cents': pledge.attribute('total_historical_amount_cents'),
			'amount_cents': reward_tier
		})

sorted_pledges = sorted(
		pledges_info,
		key=lambda pledge: pledge['total_historical_amount_cents'],
		reverse=True
)

supporter_range = [300,499]
official_patron_range = [500,1499]
super_patron_range = [1500,4999]
vip_patron_range = [5000,9999]
bronze_sponsor_range = [10000,49999]
silver_sponsor_range = [50000,999999999]

supporter_tier = [ pledge['full_name'] for pledge in sorted_pledges if pledge['amount_cents'] >= supporter_range[0] and pledge['amount_cents'] <= supporter_range[1] ]
official_patron_tier = [ pledge['full_name'] for pledge in sorted_pledges if pledge['amount_cents'] >= official_patron_range[0] and pledge['amount_cents'] <= official_patron_range[1] ]
super_patron_tier = [ pledge['full_name'] for pledge in sorted_pledges if pledge['amount_cents'] >= super_patron_range[0] and pledge['amount_cents'] <= super_patron_range[1] ]
vip_patron_tier = [ pledge['full_name'] for pledge in sorted_pledges if pledge['amount_cents'] >= vip_patron_range[0] and pledge['amount_cents'] <= vip_patron_range[1] ]
bronze_sponsor_tier = [ pledge['full_name'] for pledge in sorted_pledges if pledge['amount_cents'] >= bronze_sponsor_range[0] and pledge['amount_cents'] <= bronze_sponsor_range[1] ]
silver_sponsor_tier = [ pledge['full_name'] for pledge in sorted_pledges if pledge['amount_cents'] >= silver_sponsor_range[0] and pledge['amount_cents'] <= silver_sponsor_range[1] ]

# this is the base path for Lucas's primary desktop work station.
basePath = 'C:\\Users\\envir\\Documents\\GitHub\\GeoPix\\GP\\Assets\\patreon'

f = open("%s\\Supporters.txt"%(basePath), "w")
f.write( '\n'.join(supporter_tier) )
f.close()


f = open("%s\\Official_Patron.txt"%(basePath), "w")
f.write( '\n'.join(official_patron_tier) )
f.close()

f = open("%s\\Super_Patron.txt"%(basePath), "w")
f.write( '\n'.join(super_patron_tier) )
f.close()

f = open("%s\\VIP_Patron.txt"%(basePath), "w")
f.write( '\n'.join(vip_patron_tier) )
f.close()

f = open("%s\\Bronze_Sponsor.txt"%(basePath), "w")
f.write( '\n'.join(bronze_sponsor_tier) )
f.close()

f = open("%s\\Silver_Sponsor.txt"%(basePath), "w")
f.write( '\n'.join(silver_sponsor_tier) )
f.close()