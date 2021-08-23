import unittest

from kittrans.models import KisartUser, WayBill, WayBillSet

USERNAME = '9615641746'#'9957001832'#'9037598079'
PASSWORD = '6nn3AX2f'#'m5XFc6xl'#'aP8N8FyU'
DRIVER_ID = '21143'#'0000005699'#'0000081297'

# class TestUserLogin(unittest.TestCase):
# 	user = None

# 	def test_autenticate(self):
# 		self.__class__.user = KisartUser(USERNAME,PASSWORD)
# 		isAuthenticated = self.__class__.user.authenticate()
# 		print("\ntest_autenticate isAuthenticated="+str(isAuthenticated)+" employeeId="+str(self.__class__.user.employeeId)+" orgName="+str(self.__class__.user.orgName)+" orgType="+str(self.__class__.user.orgType))
# 		self.assertTrue(isAuthenticated)

# 	def test_get_auth_token(self):
# 		isAuthenticated =  self.__class__.user.get_auth_token()
# 		print("\ntest_get_auth_token isAuthenticated="+str(isAuthenticated)+" token="+str(self.__class__.user.token))
# 		self.assertTrue(isAuthenticated)

# 	def test_is_medorg(self):
# 		isMedorg =  self.__class__.user.get_auth_token()
# 		print("\ntest_get_auth_token isMedorg="+str(isMedorg)+" orgType="+str(self.__class__.user.orgType))
# 		self.assertTrue(isMedorg)

# class TestGetWaybill(unittest.TestCase):
# 	user = None
# 	waybill = None

# 	def test_get_waybill(self):
# 		self.__class__.user = KisartUser(USERNAME,PASSWORD)
# 		isAuthenticated = self.__class__.user.authenticate()
# 		print("\ntest_get_waybill isAuthenticated="+str(isAuthenticated)+" employeeId="+str(self.__class__.user.employeeId)+" orgName="+str(self.__class__.user.orgName)+" orgType="+str(self.__class__.user.orgType))
# 		self.assertTrue(isAuthenticated)
# 		isAuthenticated =  self.__class__.user.get_auth_token()
# 		print("\ntest_get_waybill isAuthenticated="+str(isAuthenticated)+" token="+str(self.__class__.user.token))
# 		self.assertTrue(isAuthenticated)
# 		isMedorg =  self.__class__.user.get_auth_token()
# 		print("\ntest_get_waybill isMedorg="+str(isMedorg)+" orgType="+str(self.__class__.user.orgType))
# 		self.assertTrue(isMedorg)
# 		self.__class__.waybill = WayBill(DRIVER_ID)
# 		didGetWaybill = self.__class__.waybill.get(self.__class__.user.token)
# 		print("\ntest_get_waybill didGetWaybill="+str(didGetWaybill)+" waybillId="+str(self.__class__.waybill.waybillId)+" status="+str(self.__class__.waybill.status))
# 		self.assertTrue(didGetWaybill)
# 		isWaybillStatusOk = self.__class__.waybill.is_status_ok()
# 		self.assertTrue(isWaybillStatusOk)
# 		self.__class__.waybill.waybillId = 50344
# 		isWaybillInfoLoaded = self.__class__.waybill.load_info(self.__class__.user.token)
# 		print("\ntest_get_waybill isWaybillInfoLoaded="+str(isWaybillInfoLoaded)+" dateTimeGiven="+str(self.__class__.waybill.dateTimeGiven)+" dateTimeValid="+str(self.__class__.waybill.dateTimeValid))
# 		self.assertTrue(isWaybillInfoLoaded)
# 		isPreDrivePassed = self.__class__.waybill.is_predrive_passed()
# 		isPostDrivePassed = self.__class__.waybill.is_postdrive_passed()
# 		print("\ntest_get_waybill isPreDrivePassed="+str(isPreDrivePassed)+" isPostDrivePassed="+str(isPostDrivePassed))

class TestGetWaybillSet(unittest.TestCase):
	user = None
	waybill = None

	def test_get_waybill_set(self):
		self.__class__.user = KisartUser(USERNAME,PASSWORD)
		isAuthenticated = self.__class__.user.authenticate()
		print("\ntest_get_waybill_set isAuthenticated="+str(isAuthenticated)+" employeeId="+str(self.__class__.user.employeeId)+" orgName="+str(self.__class__.user.orgName)+" orgType="+str(self.__class__.user.orgType))
		self.assertTrue(isAuthenticated)
		isAuthenticated =  self.__class__.user.get_auth_token()
		print("\ntest_get_waybill_set isAuthenticated="+str(isAuthenticated)+" token="+str(self.__class__.user.token))
		self.assertTrue(isAuthenticated)
		isMedorg =  self.__class__.user.is_medorg()
		print("\ntest_get_waybill_set isMedorg="+str(isMedorg)+" orgType="+str(self.__class__.user.orgType))
		self.assertTrue(isMedorg)
		waybill_set = WayBillSet(kisart_id=DRIVER_ID,search_query="эртекин")
		waybill_set.load_set(self.__class__.user.token)
		waybill = waybill_set.get_last_in_order()
		self.assertIsNotNone(waybill)
		
		# self.assertTrue(waybill.is_status_ok())
		# self.assertTrue(waybill.is_datetime_ok(2))
		print("waybill.waybillId "+str(waybill.waybillId)+" waybill.driver_id "+str(waybill.driver_id))
		print(waybill.is_predrive_passed())
		print(waybill.is_postdrive_passed())
		waybill_new = WayBill(DRIVER_ID)
		waybill_new.waybillId = waybill.waybillId
		print("waybill_new "+str(waybill_new.waybillId))
		isAuthenticated =  self.__class__.user.get_auth_token()
		# waybill_some= WayBill(DRIVER_ID)
		# didGetWaybill = waybill_some.get(self.__class__.user.token)
		# waybill_some.load_info(self.__class__.user.token)

		waybill_new.load_info(self.__class__.user.token)
		print(waybill_new.is_predrive_passed())
		print(waybill_new.is_postdrive_passed())


if __name__ == '__main__':
	unittest.main()