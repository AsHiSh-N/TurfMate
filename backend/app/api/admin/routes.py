from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.session import get_db
from app.models import Booking, Payment, Role, User, Venue, VenueState
router=APIRouter()
def require_admin(user, db):
	try: user_id=int(user['sub'])
	except (KeyError,TypeError,ValueError) as exc: raise HTTPException(401,'Invalid token') from exc
	account=db.query(User).filter(User.id==user_id).first()
	if not account or account.role!=Role.ADMIN: raise HTTPException(403,'Admin access required')
@router.get('/venues')
def admin_venues(db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
	require_admin(user,db)
	return {'success':True,'data':[{'id':v.id,'name':v.name,'city':v.city,'owner_id':v.owner_id,'status':v.status.value} for v in db.query(Venue).all()]}
@router.post('/venues/{venue_id}/approve')
def approve(venue_id:int,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
	require_admin(user,db)
	v=db.query(Venue).filter(Venue.id==venue_id).first()
	if not v: raise HTTPException(404,'Venue not found')
	v.status=VenueState.ACTIVE; db.commit(); return {'success':True,'data':{'id':v.id,'status':'ACTIVE'}}
@router.get('/bookings')
def admin_bookings(db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
	require_admin(user,db)
	return {'success':True,'data':[{'id':b.id,'booking_reference':b.booking_reference,'venue_id':b.venue_id,'status':b.status.value,'total_amount':b.total_amount} for b in db.query(Booking).all()]}
@router.get('/payments')
def payments(db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
	require_admin(user,db)
	return {'success':True,'data':[{'id':p.id,'booking_id':p.booking_id,'transaction_id':p.transaction_id,'amount':p.amount,'status':p.status} for p in db.query(Payment).all()]}
