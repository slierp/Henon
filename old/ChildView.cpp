// ChildView.cpp : implementation of the CChildView class
//

#include "stdafx.h"
#include "Henon.h"
#include "ChildView.h"
#include <math.h>
#include <strstrea.h>
#include "MainFrm.h"
#include "HenDialog.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CChildView

CChildView::CChildView()
{
	xleft = -1.5;
	ytop = 0.4;
	xright = 1.5;
	ybottom = -0.4;
	draw_axes = true;	
	x_subdivide = 12, //even integer number!
	y_subdivide = 8; //even integer number!
	//have to be doubles because otherwise calculations will be done integer-like
	//resulting in unwanted rounding
	Nmax = 1000000;
	limitN = 10000;
	neglectN = 1000;
	currentN = 0;
	hena = 1.4;
	henb = 0.3;
	x_overall = 0.1;
	y_overall = 0.1;
	henx = x_overall;
	heny = y_overall;
	count_drawn_points = 0;
	busymouse = false;
	alternatecbrush = false;
	draw_whole_orbit = true;
	draw_lines = false;
	exited_window = false;
	range = 0.3;
	increment = 0.01;
	just_erase_window = false;
	movie_end = henb;
	animation_running = false;
	animate_clean = true;
	which_var_to_anim = true; //true is henb
	zoom_demo_running = false;
	which_zoom_demo = 1;
}

CChildView::~CChildView()
{
}


BEGIN_MESSAGE_MAP(CChildView,CWnd )
	//{{AFX_MSG_MAP(CChildView)
	ON_WM_PAINT()
	ON_WM_LBUTTONDOWN()
	ON_WM_LBUTTONUP()
	ON_COMMAND(ID_ZOOM_OUT, OnZoomOut)
	ON_COMMAND(ID_STOP_EVALUATION, OnStopEvaluation)
	ON_COMMAND(ID_START_VDIALOG, OnStartVdialog)
	ON_WM_MOUSEMOVE()
	ON_COMMAND(ID_WHOLE_ORBIT, OnWholeOrbit)
	ON_COMMAND(ID_DRAW_LINES, OnDrawLines)
	ON_COMMAND(ID_ANIMATE, OnAnimate)
	ON_COMMAND(ID_ANIMCLEAN, OnAnimclean)
	ON_COMMAND(ID_REDRAW, OnRedraw)
	ON_COMMAND(ID_SWICTHVARTOANIM, OnSwicthvartoanim)
	ON_COMMAND(ID_DEMO1, OnDemo1)
	ON_COMMAND(ID_DEMO2, OnDemo2)
	ON_COMMAND(ID_DEMO3, OnDemo3)
	ON_COMMAND(ID_DEMO4, OnDemo4)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()


/////////////////////////////////////////////////////////////////////////////
// CChildView message handlers

BOOL CChildView::PreCreateWindow(CREATESTRUCT& cs) 
{
	if (!CWnd::PreCreateWindow(cs))
		return FALSE;

	cs.dwExStyle |= WS_EX_CLIENTEDGE;
	cs.style &= ~WS_BORDER;
	CBrush
		background_brush;
	background_brush.CreateSolidBrush(0x000000); //black brush for background color
	cs.lpszClass = AfxRegisterWndClass(CS_HREDRAW|CS_VREDRAW|CS_DBLCLKS, 
		::LoadCursor(NULL, IDC_ARROW), background_brush, NULL); //before: HBRUSH(COLOR_WINDOW+1)

	return TRUE;
}

void CChildView::OnPaint() 
{
	CMainFrame//get pointer to parent mainframe to be able to set status message
		*mainframe_ptr = static_cast<CMainFrame *>(GetParent());

	CPaintDC dc(this); // device context for painting

	double
		henxtemp;

	if(Nmax < limitN)
		limitN = Nmax;

	if(draw_axes) //call subroutine that draws axes	
		draw_them_axes(&dc);	

	if(animation_running) //print current a or b value in status bar
	{
		char
			*buffer;

		//ascertain precision from increment
		int idx;
		double value = increment;
		for(idx = 0; value < 1; idx++)
			value = value*10;
		//end ascertation

		int		
			decimal,
			sign,
			precision = idx;

		if(which_var_to_anim)
			buffer = _ecvt(henb, precision, &decimal, &sign );
		else
			buffer = _ecvt(hena, precision, &decimal, &sign );


		cs = buffer; //an = statement so we don't have to empty string for future use!

		if(decimal < 0)
			for(; decimal < 0; decimal++)
			{
				cs.Insert(0,"0");
				cs.Delete(cs.GetLength() - 1,1); //negative decimal means
			}									 //precision value was too high	
												 //so we have to delete some trailing zeros

		cs.Insert(decimal,".");

		if(sign != 0)
			cs.Insert(0,"-");

		if(which_var_to_anim)
			cs.Insert(0, "b = ");
		else
			cs.Insert(0, "a = ");

		mainframe_ptr->SetMessageText(cs); //'busy' message
	}
	else
		mainframe_ptr->SetMessageText(AFX_IDS_BUSYMESSAGE); //'busy' message

	if(draw_lines)
	{
		CPen
			lpen;
		lpen.CreatePen(PS_SOLID,1,RGB(255,255,255)); //create line pen
		dc.SelectObject(&lpen); //make lines
		dc.MoveTo((henx-xleft)*xratio,ypixelheigth-(heny-ybottom)*yratio);
		for(int idx3=0;idx3<limitN;idx3++) 
		{
			henxtemp = 1-(hena*henx*henx)+heny;
				heny = henb*henx;
			henx = henxtemp;
	
			if(count_drawn_points > (0.1*xpixelwidth*ypixelheigth)) //exit??
			{
				currentN = Nmax;
				break;
			}
	
			if(!draw_whole_orbit && currentN < neglectN)
				continue;
			
			if(xleft < henx && henx < xright && ybottom < heny && heny < ytop)
			{
				if(exited_window) //if we we're outside then only move to the new point
				{
					dc.MoveTo((henx-xleft)*xratio,ypixelheigth-(heny-ybottom)*yratio);			
					exited_window = false;
				}
				else //if previous and this point are in the window, then draw a line
					dc.LineTo((henx-xleft)*xratio,ypixelheigth-(heny-ybottom)*yratio);	
				
				count_drawn_points++;
			}
			else //we're outside the window
				exited_window = true;
		}
	}
	else
	{
		for(int idx3=0;idx3<limitN;idx3++) 
		{
			henxtemp = 1-(hena*henx*henx)+heny;
				heny = henb*henx;
			henx = henxtemp;
	
			if(count_drawn_points > (0.25*xpixelwidth*ypixelheigth))
			{
				currentN = Nmax;
				break;
			}

			if(!draw_whole_orbit && currentN < neglectN)
				continue;	

			if(xleft < henx && henx < xright && ybottom < heny && heny < ytop)
			{
				dc.SetPixel((henx-xleft)*xratio,ypixelheigth-(heny-ybottom)*yratio, 
					RGB(255,255,255));	
			
				count_drawn_points++;
			}
		}
	}

	currentN += limitN;
	draw_axes = false;
	if(currentN < Nmax) //if Nmax has not been reached	
		Invalidate(0);	
	else //if done with current drawing or stopped by esc
	{
		if(animation_running)
		{
			if(!make_movie())
				mainframe_ptr->SetMessageText(AFX_IDS_IDLEMESSAGE); //'ready' message
		}
		else if(zoom_demo_running)
		{
			if(which_zoom_demo == 1)
				OnDemo2();
			else
				OnDemo4();

			mainframe_ptr->SetMessageText(AFX_IDS_ZOOM_DEMOMESSAGE);
		}
		else
			mainframe_ptr->SetMessageText(AFX_IDS_IDLEMESSAGE); //'ready' message		
	}
} //end of OnPaint

void CChildView::reset_window_dimensions()
{
	GetClientRect(&Window_Rect);

	xpixelwidth = Window_Rect.right,
	ypixelheigth = Window_Rect.bottom;

	xratio = fabs(xpixelwidth/(xright-xleft)); //ratio screenwidth to valuewidth
	yratio = fabs(ypixelheigth/(ytop-ybottom));
}

void CChildView::draw_them_axes(CPaintDC *dc)
{
	GetClientRect(&Window_Rect); //fill rectangle with window or vice versa
	dc->FillSolidRect(&Window_Rect,RGB(0,0,0)); //erase window

	if(just_erase_window) //quit now if you just want to erase the window
	{
		just_erase_window = false;
		return;
	}

	reset_window_dimensions();

	double
		xvaluebit = fabs((xright-xleft)/x_subdivide), //increment sizes of axes values
		yvaluebit = fabs((ytop-ybottom)/y_subdivide),
		halfx = xpixelwidth, //positions of axes are halfway the window
		halfy = ypixelheigth;
	halfx = (halfx/2);
	halfy = (halfy/2);

	double		
		xaxesbit = (xpixelwidth/x_subdivide), //increment sizes of axes delimiter stripes
		yaxesbit = (ypixelheigth/y_subdivide);

	//TO DO: convert to different fontsizes depending on number of pixels available
	//and convert axes number drawing more like in OnPaint (with CString)
	
	CPen assenpen;
	assenpen.CreatePen(PS_SOLID,1,RGB(150,150,255)); //create gray pen
	dc->SelectObject(&assenpen); //make axes
	dc->MoveTo(0,halfy);
	dc->LineTo(xpixelwidth,halfy);
	dc->MoveTo(halfx,0);
	dc->LineTo(halfx,ypixelheigth);
	dc->SetTextColor(RGB(150,150,255));

	double
		draw;

	char *chardraw = new char[20];
		
	RECT getalplek;

	int
		l;

	for(unsigned int idx=1;idx<x_subdivide;idx++) //x-axes
	{
		dc->MoveTo(idx*xaxesbit,halfy);
		dc->LineTo(idx*xaxesbit,halfy+8);
		draw = xleft+(idx*xvaluebit);		

		strstream
			convstrings;

		convstrings << draw;
		convstrings >> chardraw;

		l = strlen(chardraw);
	
		getalplek.left = (idx*xaxesbit)-10;
		getalplek.right = (idx*xaxesbit)+((l-1)*8);
		getalplek.top = halfy+8;
		getalplek.bottom = halfy+28;
	
		dc->DrawText(chardraw,-1,&getalplek,DT_LEFT | DT_SINGLELINE | DT_NOCLIP);
	}
	for(unsigned int idx2=1;idx2<y_subdivide;idx2++) //y-axes
	{
		if(idx2 == (y_subdivide/2)) //skip xy crosspoint
			continue;

		dc->MoveTo(halfx,idx2*yaxesbit);		
		dc->LineTo(halfx-8,idx2*yaxesbit);

		draw = ytop-(idx2*yvaluebit);		

		strstream
			convstrings;

		convstrings << draw;				
		convstrings >> chardraw;

		l = strlen(chardraw);
	
		getalplek.left = halfx-100;
		getalplek.right = halfx-8;
		getalplek.top = (idx2*yaxesbit)-10;
		getalplek.bottom = (idx2*yaxesbit)+10;

		dc->DrawText(chardraw,-1,&getalplek,DT_RIGHT | DT_SINGLELINE | DT_NOCLIP);
	}

	delete chardraw;
	draw_axes = false; //return to false mode after draw
} //end of draw_them_axes

void CChildView::reinitialize() //called by mainframe on window size change
{	//and by childframe when it (re)gains focus
	draw_axes = true;
	just_erase_window = false;
	currentN = 0;
	count_drawn_points = 0;
	henx = x_overall;
	heny = y_overall;

	if(animation_running)
	{
		if(which_var_to_anim)
		{
			henb = movie_end - (0.5*range); //reset henb to original value
			movie_end = henb;
			animation_running = false; //end of animation
		}
		else
		{
			hena = movie_end - (0.5*range); //reset henb to original value
			movie_end = hena;
			animation_running = false; //end of animation
		}
	}
}

void CChildView::OnLButtonDown(UINT nFlags, CPoint point) 
{
	if(animation_running)
		return;

	CWnd ::OnLButtonDown(nFlags, point);
	MSelecStart = point;
}

void CChildView::OnMouseMove(UINT nFlags, CPoint point) 
{
	if(animation_running)
		return;
	
	CWnd ::OnMouseMove(nFlags, point);

	if(!(nFlags & MK_LBUTTON)) //return if left mouse button is not down
		return;

	CClientDC aDC(this); //get handle to window
		
	CSize
		sz(1,1); //thickness of rectangle
	
	CBrush
		*brush_ptr1 = &dragrectbrush1, //pointers to member variable brushes
		*brush_ptr2 = &dragrectbrush2;
	
	if(!busymouse) //if we're starting the first rectangle
	{		
		CRect
			temp(MSelecStart,point), //first rectangle
			*drag_rect_ptr = 0;

		drag_rect.CopyRect(temp); //copy new rect to oldrect

		drag_rect_ptr = &drag_rect;
		
		aDC.DrawDragRect(drag_rect_ptr,sz,NULL,sz,brush_ptr1,NULL);
						//draw rect; old rect does not exist and is thus NULL
		MSelecEnd = point; //adjust endpoint
	}
	else
	{
		CRect
			new_rect(MSelecEnd,point),
			*new_rect_ptr = &new_rect,
			*drag_rect_ptr = &drag_rect;

		if(!alternatecbrush)
		{
			aDC.DrawDragRect(new_rect_ptr,sz,drag_rect_ptr,sz,brush_ptr2,brush_ptr1);	
			alternatecbrush = true;
		}
		else
		{
			aDC.DrawDragRect(new_rect_ptr,sz,drag_rect_ptr,sz,brush_ptr1,brush_ptr2);	
			alternatecbrush = false;
		}

		drag_rect.CopyRect(new_rect);
	}

	busymouse = true;	
} //end of OnMouseMove

void CChildView::OnLButtonUp(UINT nFlags, CPoint point) 
{
	if(animation_running)
		return;
	
	CWnd ::OnLButtonUp(nFlags, point);

	CSize
		diff = MSelecStart - point;
	
	busymouse = false;

	if((abs(diff.cx) < 10 && abs(diff.cy) < 10) || (MSelecStart.x == 0 && MSelecStart.y == 0))
	//if end and start (almost) coincide, keep image; Start == 0 rule works but is obscure
		return;

	MSelecEnd=point;

	if(MSelecStart.x < MSelecEnd.x)
	{	
		xright = (MSelecEnd.x/xratio) + xleft; //rules have to be in this order
		xleft = (MSelecStart.x/xratio) + xleft; //because xleft is used in them both
	}
	else
	{
		xright = (MSelecStart.x/xratio) + xleft;
		xleft = (MSelecEnd.x/xratio) + xleft;
	}

	if(MSelecStart.y < MSelecEnd.y)
	{
		ytop = ((-MSelecStart.y + ypixelheigth)/yratio) + ybottom;
		ybottom = ((-MSelecEnd.y + ypixelheigth)/yratio) + ybottom;
	}
	else
	{
		ytop = ((-MSelecEnd.y + ypixelheigth)/yratio) + ybottom;
		ybottom = ((-MSelecStart.y + ypixelheigth)/yratio) + ybottom;
	}

	OnRedraw();
} //end of OnMouseButtonUp

void CChildView::OnZoomOut() 
{
	if(animation_running)
		return;

	xleft = -1.5;
	ytop = 0.4;
	xright = 1.5;
	ybottom = -0.4;
	OnRedraw();
}

void CChildView::OnStopEvaluation() 
{
	CMainFrame//get pointer to parent mainframe to be able to set status message
		*mainframe_ptr = static_cast<CMainFrame *>(GetParent());

	reinitialize();
	zoom_demo_running = false; //also stop this demo if running
	ValidateRect(&Window_Rect);
	mainframe_ptr->SetMessageText(AFX_IDS_IDLEMESSAGE); //'ready' message	
}

void CChildView::OnStartVdialog() 
{
	if(animation_running)
		return;

	CHenDialog
		dialog;

	dialog.m_hena = hena;
	dialog.m_henb = henb;
	dialog.m_henN = Nmax;
	dialog.m_henincr = increment;
	dialog.m_henrange = range;
	dialog.m_henXLeft = xleft;
	dialog.m_henXRight = xright;
	dialog.m_henYTop = ytop;
	dialog.m_henYBottom = ybottom;
	dialog.m_henNlimit = limitN;
	dialog.m_henneglectN = neglectN;

	if(dialog.DoModal() != IDOK)
		return;//do this only when ok is clicked

	hena = dialog.m_hena;
	henb = dialog.m_henb;
	increment = dialog.m_henincr;	
	range = dialog.m_henrange;
	limitN = dialog.m_henNlimit;


	if(dialog.m_henneglectN < dialog.m_henN)
	{
		neglectN = dialog.m_henneglectN;
		Nmax = dialog.m_henN;
	}

	if(dialog.m_henXRight != xright || dialog.m_henYTop != ytop ||
		dialog.m_henYBottom != ybottom || dialog.m_henNlimit != limitN)
	//reassert the size of the window
		reset_window_dimensions();
		
	if(dialog.m_henXLeft < dialog.m_henXRight)
	{
		xleft = dialog.m_henXLeft;
		xright = dialog.m_henXRight;
	}

	if(dialog.m_henYTop > dialog.m_henYBottom)
	{
		ytop = dialog.m_henYTop;
		ybottom = dialog.m_henYBottom;
	}
}

void CChildView::OnWholeOrbit() 
{
	if(animation_running)
		return;

	if(draw_whole_orbit) //switch bool
		draw_whole_orbit = false;
	else
		draw_whole_orbit = true;
}

void CChildView::OnDrawLines() 
{
	if(animation_running)
		return;

	if(draw_lines) //switch bool
		draw_lines = false;
	else
		draw_lines = true;		
}

bool CChildView::make_movie() //only called when animation_running is true
{
	if(which_var_to_anim)
	{
		if(henb >= movie_end)
		{//if animation was running and henb has reached or crossed the limit value movie_end
			reinitialize();
			return(false);
		}
		else //animation must be running and henb must be below limit value
		{
			henb += increment;
			currentN = 0;
			count_drawn_points = 0;
			henx = x_overall;
			heny = y_overall;
			Invalidate(0);
			if(animate_clean)
			{
				draw_axes = true;
				just_erase_window = true;
			}
			else		
				draw_axes = false;
		}

		return(true);
	}
	else
	{
		if(hena >= movie_end)
		{//if animation was running and henb has reached or crossed the limit value movie_end
			reinitialize();
			return(false);
		}
		else //animation must be running and henb must be below limit value
		{
			hena += increment;
			currentN = 0;
			count_drawn_points = 0;
			henx = x_overall;
			heny = y_overall;
			Invalidate(0);
			if(animate_clean)
			{
				draw_axes = true;
				just_erase_window = true;
			}
			else		
				draw_axes = false;
		}

		return(true);
	}
}

void CChildView::OnAnimate() 
{
	if(animation_running)
		return;

	draw_lines = false; //seems to be safe, but only leads to mumbo-jumbo screen, so disable it
	just_erase_window = true; //erases screen rather than draw complete axes
	draw_axes = true;
	animation_running = true;
	if(which_var_to_anim)
	{
		movie_end = henb + (0.5*range);
		henb -= (0.5*range);
	}
	else
	{
		movie_end = hena + (0.5*range);
		hena -= (0.5*range);
	}
	Invalidate(0);
}

void CChildView::OnAnimclean() 
{
	if(animation_running)
		return;

	if(animate_clean) //switch bool
		animate_clean = false;
	else
		animate_clean = true;
}

void CChildView::OnRedraw() 
{
 	reinitialize();
 	Invalidate(0);	
}

void CChildView::OnSwicthvartoanim() 
{
	if(animation_running)
		return;

	if(which_var_to_anim) //switch bool
		which_var_to_anim = false;
	else
		which_var_to_anim = true;	
}

void CChildView::OnDemo1() 
{
	if(animation_running)
		return;

	which_var_to_anim = true;
	draw_whole_orbit = false;
	hena = 1.4;
	henb = -0.05;
	Nmax = 50000;
	limitN = 10000;
	neglectN = 1000;
	increment = 0.005;
	range = 0.7;
	xleft = -1.5;
	xright = 1.5;
	ytop = 0.4;
	ybottom = -0.4;
	animate_clean = true;
	reset_window_dimensions();
	OnAnimate();
}
void CChildView::OnDemo2()  //zoom demo 1
{
	if(animation_running)
		return;

	if(!zoom_demo_running)
	{
		xleft = -1.5; xright = 1.5;	ytop = 0.4;	ybottom = -0.4;
		zoom_demo_running = true;
		which_zoom_demo = 1;
		Invalidate(0);
	}
	else if(xleft == -1.5)
	{
		xleft = 0.10537; ybottom = 0.110629; xright = 0.50537; ytop = 0.310629;
	}
	else if(xleft == 0.10537)
	{
		xleft = 0.28537; ybottom = 0.200629; xright = 0.32537; ytop = 0.220629;
	}
	else
	{
		xleft = 0.30337; ybottom = 0.209629; xright = 0.30737; ytop = 0.211629;
		zoom_demo_running = false;
	}

	draw_lines = false;
	draw_whole_orbit = false;
	hena = 1.4;
	henb = 0.3;
	Nmax = 10000000;
	limitN = 10000;
	neglectN = 1000;
	draw_axes = true;
	just_erase_window = false;
	reinitialize();
}

void CChildView::OnDemo3() 
{
	if(animation_running)
		return;

	which_var_to_anim = false;
	draw_whole_orbit = false;
	hena = 0.75;
	henb = 0.4;
	Nmax = 50000;
	limitN = 10000;
	increment = 0.005;
	neglectN = 1000;
	range = 1;
	xleft = -1.5;
	xright = 1.8;
	ytop = 0.7;
	ybottom = -0.7;
	animate_clean = true;
	reset_window_dimensions();
	OnAnimate();
}

void CChildView::OnDemo4() //zoom demo 2
{
	if(animation_running)
		return;

	if(!zoom_demo_running)
	{
		xleft = -1.5; xright = 1.5;	ytop = 0.4;	ybottom = -0.4;
		zoom_demo_running = true;
		which_zoom_demo = 2;
		Invalidate(0);
	}
	else
	{
		xleft = 0.1029; ybottom = -0.2479; xright = 0.8147; ytop = -0.03067;
		zoom_demo_running = false;
	}

	draw_lines = true;
	draw_whole_orbit = true;
	hena = 1.4;
	henb = -0.3;
	Nmax = 10000000;
	limitN = 10000;
	draw_axes = true;
	just_erase_window = false;
	reinitialize();
}
