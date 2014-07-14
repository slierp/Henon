// ChildView.h : interface of the CChildView class
//
/////////////////////////////////////////////////////////////////////////////

#if !defined(AFX_CHILDVIEW_H__E5110BAC_519A_11D4_956A_95EEACA92421__INCLUDED_)
#define AFX_CHILDVIEW_H__E5110BAC_519A_11D4_956A_95EEACA92421__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

/////////////////////////////////////////////////////////////////////////////
// CChildView window

class CChildView : public CWnd
{
// Construction
public:
	CChildView();

// Attributes
public:

// Operations
public:

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CChildView)
	protected:
	virtual BOOL PreCreateWindow(CREATESTRUCT& cs);
	//}}AFX_VIRTUAL

// Implementation
public:
	CPoint MSelecEnd;
	CPoint MSelecStart;
	double y_subdivide;
	bool draw_whole_orbit;
	bool draw_lines;
	bool animate_clean;

	virtual ~CChildView();

	// Generated message map functions
protected:
	//{{AFX_MSG(CChildView)
	afx_msg void OnPaint();
	afx_msg void OnLButtonDown(UINT nFlags, CPoint point);
	afx_msg void OnLButtonUp(UINT nFlags, CPoint point);
	afx_msg void OnZoomOut();
	afx_msg void OnStopEvaluation();
	afx_msg void OnStartVdialog();
	afx_msg void OnMouseMove(UINT nFlags, CPoint point);
	afx_msg void OnWholeOrbit();
	afx_msg void OnDrawLines();
	afx_msg void OnAnimate();
	afx_msg void OnAnimclean();
	afx_msg void OnRedraw();
	afx_msg void OnSwicthvartoanim();
	afx_msg void OnDemo1();
	afx_msg void OnDemo2();
	afx_msg void OnDemo3();
	afx_msg void OnDemo4();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
private:
	short which_zoom_demo;
	long int neglectN;
	CString cs;
	bool zoom_demo_running;
	void reset_window_dimensions();
	int limitN;
	bool which_var_to_anim;
	void reinitialize();
	bool animation_running;
	double range;
	bool just_erase_window;
	double movie_end;
	double increment;
	bool make_movie();
	bool exited_window;
	double y_overall;
	double x_overall;
	CRect drag_rect;
	bool alternatecbrush;
	CBrush dragrectbrush2;
	CBrush dragrectbrush1;
	bool busymouse;
	unsigned int count_drawn_points;
	RECT Window_Rect;
	void OnDraw(CDC *);
	double heny;
	double henx;
	long unsigned currentN;
	long unsigned Nmax;
	double henb;
	double hena;
	double yratio;
	double xratio;
	unsigned int ypixelheigth;
	unsigned int xpixelwidth;
	void draw_them_axes(CPaintDC *);
	double x_subdivide;
	bool draw_axes;
	double ybottom;
	double ytop;
	double xright;
	double xleft;
};

/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CHILDVIEW_H__E5110BAC_519A_11D4_956A_95EEACA92421__INCLUDED_)
