from math import *
import numpy as np
import sys

# Geo parameters
global re
global aWGS84, bWGS84, e2WGS84, nWGS84
global FOUTM

re = 6371.009 # mean earth radius in Km (IUGG)
aWGS84 = 6378.1370000
bWGS84 = 6356.7523142
e2WGS84 = 1.0 - bWGS84*bWGS84/aWGS84/aWGS84
nWGS84 = (aWGS84-bWGS84)/(aWGS84+bWGS84)
F0UTM = 0.9996

def GetLatLong(clatlong, distxy):
  # Gets the lat and long of a point distxy km north/east of clatlong (approximate due to orthographic projection)

  clat = clatlong[0]*pi/180.0
  clong = clatlong[1]*pi/180.0
  x2 = cos(clat)
  z2 = sin(clat)
  y = 0
  
  x = x2 - sin(clat)*distxy[1]/re
  z = z2 + cos(clat)*distxy[1]/re
  y = distxy[0]/re
  
  d = sqrt(x*x+y*y+z*z)
  dp = sqrt(x*x+y*y)
  x=x/dp
  y=y/dp
  z=z/d
  
  elat=asin(z)
  elong=mod(2.0*pi + clong + atan2(y,x),2.0*pi)
  
  lat = elat*180.0/pi
  lon = elong*180.0/pi
  
  return [lat,lon]

#####

def nu_TM(lat):
  # nu function for transverse mercator conversions
  
  s = sin(lat)
  s2 = s*s
  t = 1.0 - e2WGS84*s2
  
  nu = aWGS84*F0UTM/sqrt(t)
  
  return nu

#####

def rho_TM(lat):
  # rho function for transverse mercator conversions
  
  s = sin(lat)
  s2 = s*s
  t = 1.0 - e2WGS84*s2
  
  rho = aWGS84*F0UTM*(1.0-e2WGS84)/t/sqrt(t)
  
  return rho

#####

def M_TM(lat,lat0):
  # M function for transverse mercator conversions
  
  dif = lat-lat0
  add = lat+lat0
  
  tn1 = 1.0 + nWGS84 + 1.25*nWGS84*nWGS84*(1.0 + nWGS84)
  
  tn2 = 3.0*nWGS84*(1.0 + nWGS84) + 21.0/8.0*nWGS84*nWGS84*nWGS84
  
  tn3 = 15.0/8.0*nWGS84*nWGS84*(1.0 + nWGS84)
  
  tn4 = 35.0/24.0*nWGS84*nWGS84*nWGS84
  
  M = bWGS84*F0UTM*( tn1*dif - tn2*sin(dif)*cos(add) + tn3*sin(2.0*dif)*cos(2.0*add) - tn4*sin(3.0*dif)*cos(3.0*add) )
  
  return M

#####

def EastingNorthing_TM(clatlong,latlong):
  # Gets the easting and northing of a point latlong relative to an origin at clatlong using a Transverse Mercator projection
  
  clat = clatlong[0]*pi/180.0
  clong = clatlong[1]*pi/180.0
  
  lat = latlong[0]*pi/180.0
  lon = latlong[1]*pi/180.0
  
  dl = lon-clong
  dl2 = dl*dl
  dl3 = dl2*dl
  dl4 = dl2*dl2
  dl5 = dl4*dl
  dl6 = dl3*dl3
  
  nu = nu_TM(lat)
  
  rho = rho_TM(lat)
  
  eta2 = nu/rho - 1.0
  
  sn = sin(lat)
  cs = cos(lat)
  tn = sn/cs
  
  t1 = M_TM(lat,clat)
  
  t2 = 0.5*nu*sn*cs
  
  cs3 = cs*cs*cs
  tn2 = tn*tn
  t3 = nu/24.0*sn*cs3*(5.0-tn2+9.0*eta2)
  
  cs5 = cs3*cs*cs
  tn4 = tn2*tn2
  t31 = nu/720*sn*cs5*(61.0-58.0*tn2 + tn4)
  
  t4 = nu*cs
  
  t5 = nu/6.0*cs3*(nu/rho - tn2)
  
  t6 = nu/120.0*cs5*(5.0 - 18.0*tn2 + tn4 + 14.0*eta2 - 58.0*tn2*eta2)
  
  disty = t1 + t2*dl2 + t3*dl4 + t31*dl6
  distx = t4*dl + t5*dl3 + t6*dl5
  
  return [distx,disty]

#####

def LatLon_TM(clatlong,distxy,unit='km'):
  # Gets the latitude and longitude of a point distxy relative to an origin at clatlong using a Transverse Mercator projection
  
  clat = clatlong[0]*pi/180.0
  clong = clatlong[1]*pi/180.0
  
  E = distxy[0]
  N = distxy[1]
  if unit=='m':
    E = E/1e3
    N = N/1e3
  
  E2 = E*E
  E3 = E*E2
  E4 = E2*E2
  E5 = E2*E3
  E6 = E3*E3
  E7 = E3*E4
  
  lat = N/aWGS84/F0UTM + clat
  M = M_TM(lat,clat)
  #er = abs(N-M)
  er = 1
  
  j=1
  while (er>1e-8):
    lat0 = lat
    lat = (N-M)/aWGS84/F0UTM + lat0
    M = M_TM(lat,clat)
    er = abs(N-M)
    j += 1
    
    if (j==100):
      sys.exit("Failed to converge in LatLon_TM")
  
  nu = nu_TM(lat)
  nu2 = nu*nu
  nu3 = nu2*nu
  nu5 = nu2*nu3
  nu7 = nu2*nu5
  
  rho = rho_TM(lat)
  
  eta2 = nu/rho - 1.0
  
  sn = sin(lat)
  cs = cos(lat)
  tn = sn/cs
  sc = 1.0/cs
  
  t7 = 0.5*tn/rho/nu
  
  tn2 = tn*tn
  t8 = tn/24.0/rho/nu3*(5.0 + 3.0*tn2 + eta2 - 9.0*tn2*eta2)
  
  tn4 = tn2*tn2
  t9 = tn/720.0/rho/nu5*(61.0 + 90.0*tn2 + 45.0*tn4)
  
  t10 = sc/nu
  
  t11 = sc/6.0/nu3*(nu/rho + 2.0*tn2)
  
  t12 = sc/120.0/nu5*(5.0 + 28.0*tn2 + 24.0*tn4)
  
  tn6 = tn2*tn4
  t121 = sc/5040.0/nu7*(61.0 + 662.0*tn2 + 1320.0*tn4 + 720.0*tn6)
  
  lat = lat - t7*E2 + t8*E4 - t9*E6
  lon = clong + t10*E - t11*E3 + t12*E5 - t121*E7
  
  lon = fmod(2.0*pi + lon, 2.0*pi)
  #lon = (2.0*pi + lon) % (2.0*pi)
  
  lat = lat*180.0/pi
  lon = lon*180.0/pi
  
  return [lat,lon]

def LatLon_TM_polygonize(polygon,clatlong,unit='km'):
    from shapely.geometry import Polygon
    # x,y = polygon.boundary.coords.xy
    x,y = polygon.exterior.xy
    ll = []
    for (xx,yy) in zip(x,y):
        (lat,lon) = LatLon_TM(clatlong,[xx,yy],unit=unit)
        ll.append([lon,lat])
    ll_polygon = Polygon(ll)
    return ll_polygon
