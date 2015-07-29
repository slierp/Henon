// HenDialog.cpp : implementation file
//

#include "stdafx.h"
#include "Henon.h"
#include "HenDialog.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CHenDialog dialog


CHenDialog::CHenDialog(CWnd* pParent /*=NULL*/)
	: CDialog(CHenDialog::IDD, pParent)
{
	//{{AFX_DATA_INIT(CHenDialog)
	m_hena = 0.0;
	m_henb = 0.0;
	m_henN = 0.0;
	m_henincr = 0.0;
	m_henrange = 0.0;
	m_henXLeft = 0.0;
	m_henXRight = 0.0;
	m_henYBottom = 0.0;
	m_henYTop = 0.0;
	m_henNlimit = 0;
	m_henneglectN = 0;
	//}}AFX_DATA_INIT
}


void CHenDialog::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CHenDialog)
	DDX_Text(pDX, IDC_HENA, m_hena);
	DDV_MinMaxDouble(pDX, m_hena, -5., 5.);
	DDX_Text(pDX, IDC_HENB, m_henb);
	DDV_MinMaxDouble(pDX, m_henb, -5., 5.);
	DDX_Text(pDX, IDC_HENN, m_henN);
	DDV_MinMaxDouble(pDX, m_henN, 1., 9999999999999.);
	DDX_Text(pDX, IDC_INCREMENT, m_henincr);
	DDV_MinMaxDouble(pDX, m_henincr, 1.e-006, 0.2);
	DDX_Text(pDX, IDC_RANGE, m_henrange);
	DDV_MinMaxDouble(pDX, m_henrange, 1.e-004, 2.);
	DDX_Text(pDX, IDC_XLeft, m_henXLeft);
	DDX_Text(pDX, IDC_XRight, m_henXRight);
	DDX_Text(pDX, IDC_YBottom, m_henYBottom);
	DDX_Text(pDX, IDC_YTop, m_henYTop);
	DDX_Text(pDX, IDC_Nlimit, m_henNlimit);
	DDV_MinMaxInt(pDX, m_henNlimit, 1, 2147483647);
	DDX_Text(pDX, IDC_neglectN, m_henneglectN);
	DDV_MinMaxLong(pDX, m_henneglectN, 0, 1000000);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CHenDialog, CDialog)
	//{{AFX_MSG_MAP(CHenDialog)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CHenDialog message handlers



