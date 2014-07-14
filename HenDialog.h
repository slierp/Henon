#if !defined(AFX_HENDIALOG_H__2AE47020_51ED_11D4_956A_FE76DDE79921__INCLUDED_)
#define AFX_HENDIALOG_H__2AE47020_51ED_11D4_956A_FE76DDE79921__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// HenDialog.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CHenDialog dialog

class CHenDialog : public CDialog
{
// Construction
public:
	CHenDialog(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CHenDialog)
	enum { IDD = IDD_VARIABLE_DIALOG };
	double	m_hena;
	double	m_henb;
	double	m_henN;
	double	m_henincr;
	double	m_henrange;
	double	m_henXLeft;
	double	m_henXRight;
	double	m_henYBottom;
	double	m_henYTop;
	int		m_henNlimit;
	long	m_henneglectN;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CHenDialog)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CHenDialog)
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_HENDIALOG_H__2AE47020_51ED_11D4_956A_FE76DDE79921__INCLUDED_)
