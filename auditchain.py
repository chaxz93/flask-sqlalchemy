import binascii, codecs, datetime, hashlib, logging, os, pprint, json, re, requests, subprocess
from base64 import b64encode
from flask import flash, Flask, jsonify, redirect, render_template, request, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BIGINT, Boolean, Column, create_engine, DateTime, desc, Float, ForeignKey, Integer, MetaData, or_, String, Table, update  
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.utils import secure_filename

log = logging.getLogger('Auditchain')

class Auditchain():
    __id_count = 0

    def __init__(self,
        rpcuser,
        rpcpasswd,
        rpchost,
        rpcport,
        chainname,
        rpc_call=None
    ):
        self.__rpcuser = rpcuser
        self.__rpcpasswd = rpcpasswd
        self.__rpchost = rpchost
        self.__rpcport = rpcport
        self.__chainname = chainname
        self.__auth_header = ' '.join(
            ['Basic', b64encode(':'.join([rpcuser, rpcpasswd]).encode()).decode()]
        )
        self.__headers = {'Host': self.__rpchost,
            'User-Agent': 'auditchain v0.1',
            'Authorization': self.__auth_header,
            'Content-type': 'application/json'
            }
        self.__rpc_call = rpc_call

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError
        if self.__rpc_call is not None:
            name = "%s.%s" % (self.__rpc_call, name)
        return Auditchain(self.__rpcuser,
            self.__rpcpasswd,
            self.__rpchost,
            self.__rpcport,
            self.__chainname,
            name)

    def __call__(self, *args):
        Auditchain.__id_count += 1
        postdata = {'chain_name': self.__chainname,
            'version': '1.1',
            'params': args,
            'method': self.__rpc_call,
            'id': Auditchain.__id_count}
        url = ''.join(['http://', self.__rpchost, ':', self.__rpcport])
        encoded = json.dumps(postdata)
        log.info("Request: %s" % encoded)
        r = requests.post(url, data=encoded, headers=self.__headers)
        if r.status_code == 200:
            log.info("Response: %s" % r.json())
            return r.json()['result']
        else:
            log.error("Error! Status code: %s" % r.status_code)
            log.error("Text: %s" % r.text)
            log.error("Json: %s" % r.json())
            return r.json()

rpcuser = 'multichainrpc'
rpcpasswd = 'GX6CtuaRHbXXgDzFGKKfbMNwYfoX3ewNpeVA9Vd2w4E5'
rpchost = '127.0.0.1'
rpcport = '7314'
chainname = 'auditchain'

api = Auditchain(rpcuser, rpcpasswd, rpchost, rpcport, chainname)


rpc_getinfo = api.getinfo()

#dumps the json object into an element
json_str = json.dumps(rpc_getinfo)

#load the json to a string
resp = json.loads(json_str)

#extract an element in the response
#current_blocks = (resp['blocks'])
current_blocks = resp['blocks']

#extracts the full range of blocks produced
small_block = f"0-{current_blocks}"

rpc_getpeerinfo = api.getpeerinfo()
rpc_listassets = api.listassets()
rpc_listblocks = api.listblocks(small_block)
rpc_getaddresses = api.getaddresses()
rpc_multibalances = api.getmultibalances("*", "USD")

block_hash_array = []
for item in rpc_listblocks:
    block_hash_array.append(item['hash'])

testarray = list(range(0, current_blocks+1))

rpc_bareblocks = list(zip(testarray, block_hash_array))

##########################################################3
#end of flask beginigng of sqlalchemy

app = Flask(__name__)
database_url = 'postgres://zpdwrilsgqlmiu:9cbfcf3caaff842ce01ff866557c744a24af18f5da1b091af4411d5f5499a09c@ec2-184-73-222-192.compute-1.amazonaws.com:5432/dch607fni9d68p'
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

engine = create_engine(database_url, convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()

Base.query = db_session.query_property()

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    tx_date = Column(DateTime)
    txn_type = Column(String(50))
    doc_num = Column(Integer)
    is_no_post = Column(Boolean) 
    name = Column(String(50))
    memo = Column(String(50))
    credit_account_id = Column(BIGINT, ForeignKey("accounts.id"))
    credit_account = relationship("Account", foreign_keys=[credit_account_id])
    debit_account_id = Column(BIGINT, ForeignKey("accounts.id"))     
    debit_account = relationship("Account", foreign_keys=[debit_account_id])
    company_id = "Auditchain"
    amount = Column(Float)

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    balance = Column(Float)

qbo_acct_names_unique = []

for d in db_session.query(Transaction).distinct(Transaction.debit_account_id).all():
    debits = (d.__dict__)
    quickbooks_online = (debits['debit_account_id']) 
    qbo_acct_names_unique.append(quickbooks_online)

for c in db_session.query(Transaction).distinct(Transaction.credit_account_id).all():
    credits = (c.__dict__)
    quickbooks = (credits['credit_account_id']) 
    qbo_acct_names_unique.append(quickbooks)
 
qbo_acct_names_unique.pop()
qbo_unique = list(set(qbo_acct_names_unique))
acccout_set = db_session.query(Account).all()
outer_array1 = []

for q in qbo_unique:
	for a in acccout_set:
		if q == a.id:
			inner_circle1 = {}
			inner_circle1['id'] = q
			inner_circle1['accountName'] = a.name
			json_inner1 = json.dumps(inner_circle1, indent=4, sort_keys=True, default=str)
			outer_array1.append(json_inner1) 

l = 0
while l < len(outer_array1):
#	print(outer_array1[l])
	l = l+1

#print (f'Ending Array Length: {len(outer_array1)}')

active_addresses = {
    "Chase 1957 (Debit)": "1EKu91dzRTisAF4ZdBQ9gzwpmY6bDC3HHZnvCQ",
    "Realized Gains (Credit)": "1FwSwQHg1UGJGA6RH56QSfoqj3qNRVAMGh3cNx",
    "Deferred SAFT Revenue (Credit)": "1HcuPeTicjCWJszmMo1kHjFZGToFkGvnuEPwky",
    "Chase 6702 (Debit)": "13tuyQPofomieAZg9c9gXf3UWfKBE4RxC8VXat",
    "Accounts Payable (Credit)": "1T3hY9STWUkQsLQzrGgaXdMwLKLsfCqhq5uPqK",
    "Members Equity (Credit)": "1K1fCn6M59H6wNUY8JCP9A6AFRjSHehsUGxToZ",
    "Bitcoin (Debit)": "16bknt6CoT6Z8ahhTXBACHupULcBW54VJVTtmS",
    "GDAX (Debit)": "1PDgiGztvKBCiyp5dU6begH9AjSyjHfiCWNdwX",
    "Miscellaneous Cryptocurrencies (Debit)": "1TDmE1PL4GRQxdp8eSYwwxpVM35V3KhgurWMkB",
    "MyEtherWallet (Debit)": "1SyhKNEPnearnSKnc6sQZCJ6FwedJQViqVDePx",
    "Due from GMBH (Debit)": "1aFcikB9jJb7gHfghDhUzVgRoBVHCG3YYKaKgy",
    "Due from Vestcomp (Debit)": "1G7AQXLywxgQXPuKZS2hZupkaVfXCkMeCURkFM",
    "Security Deposit (Debit)": "1CQtegWgAaFgyWTiQmZxxE4otEAjjT6wcRZnj",
    "Retained Earnings (Debit)": "15xsNZjFc3femZejJk8PrqR9c4R8H6TFJGBLMC",
    "Advertising and Marketing (Debit)": "1GqrBgmRdMJDzXpF3x9LzUq5RVmxRpK1ZCgVAM",
    "Automobile Expenses (Debit)": "1S3Lo3L1Wz3McHKgodCFxd6khAt6udzLz1W6dc",
    "Bank Charges and Fees (Debit)": "1RXKAWeaxdVjpDgXkoQ9PqGL2FRwvJDqF76rsY",
    "Conferences (Debit)": "1CApwYPKa7hYufJcQnTuDyPe2cJobVZH3ra22U",
    "Dues and Subscriptions (Debit)": "1S4AmnfouSujXLEjkHjRDF1n9VK9p3tNgxTYek",
    "Insurance (Debit)": "1TqjEs6YyEoD1Jzs9J1qdwzz1wsE8ELQNz5j8g",
    "Legal and Professional Fees (Debit)": "17qrh4uRV64XwfhLV8hyCHN6FAHGXqXWtoNzyc",
    "Management Fees (Debit)": "1AkoLR58NMQF2v2PRjkAqU5ZWsWWHKZR7B5XQ5",
    "Meals and Entertainment (Debit)": "1Rgg7hPnQZsf4oTVpNhaoa3tF8NWFB6qkb4PGk",
    "Miscellaneous Expense (Debit)": "1TpBbhyCmVSmbZES4xZTcdW2hbatWezQGrYejR",
    "Office Expense (Debit)": "1PWWecwL41tESRDuvLL8oR5RJMadHHzNAPX3Y2",
    "Parking (Debit)": "1UHHqgtorTdurZsYSSaK7cv2TnSuZDxPt13pcM",
    "Rent and Lease (Debit)": "1DEs9ztsMmRRtQC1yGivEQfQHSXESUgKsAh2wV",
    "Software Development (Debit)": "1NCiUZAkp4GZ2y5fm6Xx1QpUw13Tag8nRkaa1N",
    "Subcontractors (Debit)": "15u4eYzrmYd9ygVjB5hVhd15veBPnXfEhm6upg",
    "Suspense (Debit)": "16SMYYf8UVGDLG2DHfR4CuSLJ4Sg9CCcvpnkR9",
    "Taxes and Licenses (Debit)": "1RES8ZqF56brjgr6U7Xgm9uWRVWuSy2T2jekrF",
    "Technology and Subscriptions (Debit)": "1EaQaxNY74s7XNsvapQDx3Swv7kmAszGHbBAJC",
    "Telephone and Internet (Debit)": "17ZbUNrq3ZsW8ntiNJm31TBVW6V4ee9DDreQSf",
    "Travel (Debit)": "1TSTrDZmNqyfDr1RkJVVHX9T6yu6iJME8zvHhw",
    "Utilities (Debit)": "18zQwF3wJo6LgdxhPhs2t4aEWyN9szjtBUTfuj",
    "Virtual Hosting (Debit)": "1Ln1tu5YgeV54t1wmyVPmLoWzTPfz2U9P6jkCt",
    "Charitable Contribution (Debit)": "1Gn64LLeXVCzNtt4Me8bMNKuNP8q7Y2qukUCJU"
}

modified_addresses = json.dumps(active_addresses)
loaded_r = json.loads(modified_addresses)
resp_dict = loaded_r['Suspense (Debit)'] 

dirty_accounts = {
    "Chase 1957": "1EKu91dzRTisAF4ZdBQ9gzwpmY6bDC3HHZnvCQ",
    "Deferred SAFT Revenue": "1HcuPeTicjCWJszmMo1kHjFZGToFkGvnuEPwky",
    "Chase #6702": "13tuyQPofomieAZg9c9gXf3UWfKBE4RxC8VXat",
    "Accounts Payable (A/P)": "1T3hY9STWUkQsLQzrGgaXdMwLKLsfCqhq5uPqK",
    "Members Equity": "1K1fCn6M59H6wNUY8JCP9A6AFRjSHehsUGxToZ",
    "BTC Wallet": "16bknt6CoT6Z8ahhTXBACHupULcBW54VJVTtmS",
    "GDAX": "1PDgiGztvKBCiyp5dU6begH9AjSyjHfiCWNdwX",
    "Misc. Cryptocurrencies": "1TDmE1PL4GRQxdp8eSYwwxpVM35V3KhgurWMkB",
    "My Ether Wallet": "1SyhKNEPnearnSKnc6sQZCJ6FwedJQViqVDePx",
    "Due from GMBH": "1aFcikB9jJb7gHfghDhUzVgRoBVHCG3YYKaKgy",
    "Due from Vestcomp": "1G7AQXLywxgQXPuKZS2hZupkaVfXCkMeCURkFM",
    "Security Deposit": "1CQtegWgAaFgyWTiQmZxxE4otEAjjT6wcRZnj",
    "Advertising & Marketing": "1GqrBgmRdMJDzXpF3x9LzUq5RVmxRpK1ZCgVAM",
    "Automobile Expenses": "1S3Lo3L1Wz3McHKgodCFxd6khAt6udzLz1W6dc",
    "Bank Charges & Fees": "1RXKAWeaxdVjpDgXkoQ9PqGL2FRwvJDqF76rsY",
    "Conferences": "1CApwYPKa7hYufJcQnTuDyPe2cJobVZH3ra22U",
    "Dues & Subscriptions": "1S4AmnfouSujXLEjkHjRDF1n9VK9p3tNgxTYek",
    "Insurance": "1TqjEs6YyEoD1Jzs9J1qdwzz1wsE8ELQNz5j8g",
    "Legal & Professional Fees": "17qrh4uRV64XwfhLV8hyCHN6FAHGXqXWtoNzyc",
    "Management Fees": "1AkoLR58NMQF2v2PRjkAqU5ZWsWWHKZR7B5XQ5",
    "Meals & Entertainment": "1Rgg7hPnQZsf4oTVpNhaoa3tF8NWFB6qkb4PGk",
    "Misc. Expense": "1TpBbhyCmVSmbZES4xZTcdW2hbatWezQGrYejR",
    "Office Expense": "1PWWecwL41tESRDuvLL8oR5RJMadHHzNAPX3Y2",
    "Parking": "1UHHqgtorTdurZsYSSaK7cv2TnSuZDxPt13pcM",
    "Rent & Lease": "1DEs9ztsMmRRtQC1yGivEQfQHSXESUgKsAh2wV",
    "Software Development": "1NCiUZAkp4GZ2y5fm6Xx1QpUw13Tag8nRkaa1N",
    "Subcontractors": "15u4eYzrmYd9ygVjB5hVhd15veBPnXfEhm6upg",
    "Suspense": "16SMYYf8UVGDLG2DHfR4CuSLJ4Sg9CCcvpnkR9",
    "Taxes & Licenses": "1RES8ZqF56brjgr6U7Xgm9uWRVWuSy2T2jekrF",
    "Technology Subscriptions": "1EaQaxNY74s7XNsvapQDx3Swv7kmAszGHbBAJC",
    "Telephone & Internet": "17ZbUNrq3ZsW8ntiNJm31TBVW6V4ee9DDreQSf",
    "Travel": "1TSTrDZmNqyfDr1RkJVVHX9T6yu6iJME8zvHhw",
    "Utilities": "18zQwF3wJo6LgdxhPhs2t4aEWyN9szjtBUTfuj",
    "Virtual Hosting": "1Ln1tu5YgeV54t1wmyVPmLoWzTPfz2U9P6jkCt",
    "Charitable Contribution": "1Gn64LLeXVCzNtt4Me8bMNKuNP8q7Y2qukUCJU"
} 

dirty_mod_accts = json.dumps(dirty_accounts)
load_r = json.loads(dirty_mod_accts)
dict_item = load_r['BTC Wallet'] 

entire_sets = db_session.query(Transaction).filter(Transaction.debit_account_id != None, Transaction.credit_account_id != None).all()
#largest_amount = db_session.query(Transaction).order_by(desc(Transaction.amount).limit(1)
ranked_amounts = db_session.query(Transaction).order_by(desc(Transaction.amount))

#silly_array = []
#for rnk in ranked_amounts:
#	inner_ti = {}
#	inner_ti['amount'] = rnk.amount
#	ranked_insiders = json.dumps(inner_ti, indent=4, sort_keys=True, default=str)
#	silly_array.append(ranked_insiders)
#timer = 0
#while timer < len(silly_array): 
#	print(silly_array[timer])
#	timer = timer + 1
#print (f'Transactions Ranked: {len(silly_array)}')

outer_array = []
outer_dict = {}

for per_set in entire_sets:
	inner_circle = {}
	inner_circle['company'] = per_set.company_id
	inner_circle['transaction_id'] = per_set.id
	inner_circle['transactionDate'] = per_set.tx_date.date()
	inner_circle['transactionType'] = per_set.txn_type
	inner_circle['documentNumber'] = per_set.doc_num
	inner_circle['isPosting'] = per_set.is_no_post
	inner_circle['name'] = per_set.name
	inner_circle['description'] = per_set.memo
	inner_circle['accountCredited'] = per_set.credit_account.name
	inner_circle['addressCredited'] = load_r[per_set.credit_account.name] 
	inner_circle['accountDebited'] = per_set.debit_account.name
	inner_circle['addressDebited'] = load_r[per_set.debit_account.name] 
	inner_circle['amount'] = per_set.amount
	outer_dict.update({per_set.id : inner_circle})	
	json_inner = json.dumps(inner_circle, indent=4, sort_keys=True, default=str)
	outer_array.append(json_inner)
'''
count = 0
while count < len(outer_array): 
	print(outer_array[count])
	count = count + 1
print (f'Num of transactions timestamped to auditchain: {len(outer_array)}')
'''

for dict_page in outer_dict:
	from_address = outer_dict[dict_page]['addressCredited']
	to_address = outer_dict[dict_page]['addressDebited']
	asset = "USD"
	#amount2 = str(round((outer_dict[dict_page]['amount']), 2))
	amount = outer_dict[dict_page]['amount']
	stream = "Quickbooks Online"
	key = ((outer_dict[dict_page]['transactionDate']).strftime('%m/%d/%Y')) + "|" + (((outer_dict[dict_page]['description']).replace(" ", "")).lower()) + "|" + ((outer_dict[dict_page]['name']).replace(" ", ""))
	company = "Auditchain"
	transaction_id = str(round((outer_dict[dict_page]['transaction_id']), 1)) 
	transaction_date = (outer_dict[dict_page]['transactionDate']).strftime('%m/%d/%Y')
	transaction_type = outer_dict[dict_page]['transactionType']	
	document_number = str(round((outer_dict[dict_page]['documentNumber']), 1))
	is_posting = str(outer_dict[dict_page]['isPosting'])
	name = outer_dict[dict_page]['name']
	memo = re.sub(' +', ' ',((outer_dict[dict_page]['description']).replace(" ", "")).upper())
	account_credited = (outer_dict[dict_page]['accountCredited'].replace(" ", ""))
	account_debited = (outer_dict[dict_page]['accountDebited'].replace(" ", ""))
	if amount < 0:
		print ("negative amount detected")
		absolute_amount = abs(amount)
		blockchain_timestamp_swapped = f"multichain-cli auditchain sendwithdatafrom {from_address} {to_address} '{{\"{asset}\":{absolute_amount}}}' '{{\"for\":\"{stream}\", \"key\":\"{key}\", \"data\":{{\"json\":{{\"company\":\"{company}\",\"transaction_id\":\"{transaction_id}\",\"transaction_date\":\"{transaction_date}\",\"transaction_type\":\"{transaction_type}\",\"document_number\":\"{document_number}\",\"is_posting\":\"{is_posting}\",\"name\":\"{name}\",\"memo\":\"{memo}\",\"account_credited\":\"{account_credited}\",\"account_debited\":\"{account_debited}\"}}}}}}'"
		os.system(blockchain_timestamp_swapped)
		print ("accounts swapped succesfully")
	else: 
		blockchain_timestamp = f"multichain-cli auditchain sendwithdatafrom {to_address} {from_address} '{{\"{asset}\":{amount}}}' '{{\"for\":\"{stream}\", \"key\":\"{key}\", \"data\":{{\"json\":{{\"company\":\"{company}\",\"transaction_id\":\"{transaction_id}\",\"transaction_date\":\"{transaction_date}\",\"transaction_type\":\"{transaction_type}\",\"document_number\":\"{document_number}\",\"is_posting\":\"{is_posting}\",\"name\":\"{name}\",\"memo\":\"{memo}\",\"account_credited\":\"{account_debited}\",\"account_debited\":\"{account_credited}\"}}}}}}'"
		os.system(blockchain_timestamp)

##########################################################3
#end of sqlalchemy beginning of flask

CORS(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
host = os.environ.get('IP', '127.0.0.1')
host = os.environ.get('IP', '0.0.0.0')
port = int(os.environ.get('PORT', 5000))

@app.route('/')
def index():
    return jsonify(rpc_getinfo), 200

@app.route('/getpeerinfo')
def getpeerinfo():
    return jsonify(rpc_getpeerinfo), 200

@app.route('/getaddresses')
def getaddresses():
    return jsonify(rpc_getaddresses), 200

@app.route('/listassets')
def listassets():
    return jsonify(rpc_listassets), 200

@app.route('/listblocks')
def listblocks():
    return jsonify(rpc_listblocks), 200

@app.route('/bareblocks')
def bareblocks():
    return jsonify(rpc_bareblocks), 200

@app.route('/multibalances')
def multibalances():
    return jsonify(rpc_multibalances), 200

#app.run(host=host, port=port)