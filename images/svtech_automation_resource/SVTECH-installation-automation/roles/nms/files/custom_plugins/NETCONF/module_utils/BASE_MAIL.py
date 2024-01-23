import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE , formatdate
from email import Encoders


def sendMail ( to , fro , subject , text , files = [ ] , server = "localhost" ) :
    assert type ( to ) == list
    assert type ( files ) == list

    msg = MIMEMultipart ( )
    msg [ 'From' ] = fro
    msg [ 'To' ] = COMMASPACE.join ( to )
    msg [ 'Date' ] = formatdate ( localtime = True )
    msg [ 'Subject' ] = subject
    logging.info ( '\tSending email from' + fro )
    logging.info ( '\tSending email to' + str ( to ) )

    msg.attach ( MIMEText ( text ) )

    for file in files :
        logging.info ( '\tAttaching file ' + file )
        part = MIMEBase ( 'application' , "octet-stream" )
        part.set_payload ( open ( file , "rb" ).read ( ) )
        Encoders.encode_base64 ( part )
        part.add_header ( 'Content-Disposition' , 'attachment; filename="%s"'
                          % os.path.basename ( file ) )
        msg.attach ( part )

    smtp = smtplib.SMTP ( server )
    smtp.sendmail ( fro , to , msg.as_string ( ) )
    smtp.close ( )