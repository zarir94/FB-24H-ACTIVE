import warnings
warnings.filterwarnings("ignore")
from fp.fp import FreeProxy
from requests import get as requests_get

fp = FreeProxy(rand=True)

def get(url, **kwargs):
	fp_proxy = fp.get()
	kwargs['proxies'] = {'http':fp_proxy,'https':fp_proxy}
	kwargs['verify'] = False
	return requests_get(url, **kwargs)

resp=get('https://freeipapi.com/api/json')

print(resp.text)