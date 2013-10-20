from ctypes import c_int, c_char_p, byref, sizeof
import logging
from snap7.types import S7Object, buffer_type, buffer_size, block_types,\
    wordlen_to_ctypes, BlocksList
from snap7.error import check_error
from snap7.loadlib import clib


logger = logging.getLogger(__name__)


def error_wrap(func):
    def f(*args, **kw):
        code = func(*args, **kw)
        check_error(code, client=True)
    return f


class Client(object):
    def __init__(self):
        logger.info("creating snap7 client")
        self.pointer = S7Object(clib.Cli_Create())

    #@error_wrap
    def destroy(self):
        logger.info("destroying snap7 client")
        return clib.Cli_Destroy(byref(self.pointer))

    @error_wrap
    def disconnect(self):
        logger.info("disconnecting snap7 client")
        return clib.Cli_Disconnect(self.pointer)

    @error_wrap
    def connect(self, address, rack, slot):
        logger.info("connecting to %s rack %s slot %s" % (address, rack, slot))
        return clib.Cli_ConnectTo(self.pointer, c_char_p(address),
                                  c_int(rack), c_int(slot))

    def db_read(self, db_number, start, type_, size):
        """This is a lean function of Cli_ReadArea() to read PLC DB.

        :param type_: a ctypes type

        :returns: user buffer.
        """
        logger.debug("db_read, db_number:%s, start:%s, type:%s size:%s" %
                     (db_number, start, type_, size))
        data = (type_ * size)()
        result = (clib.Cli_DBRead(self.pointer, db_number, start, size,
                                  byref(data)))
        check_error(result, client=True)
        return bytearray(data)

    @error_wrap
    def db_write(self, db_number, start, size, data):
        logger.debug("db_write db_number:%s start:%s size:%s data:%s" %
                     (db_number, start, size, data))
        return clib.Cli_DBWrite(self.pointer, db_number, start, size,
                                byref(data))

    def db_upload(self, block_type, block_num, data):
        """Uploads a block body from AG.
        """
        logger.debug("db_upload block_type: %s, block_num: %s, data: %s" %
                    (block_type, block_num, data))
        assert(block_type in block_types.values())
        size = c_int(sizeof(data))
        logger.debug("requesting size: %s" % size)
        result = clib.Cli_Upload(self.pointer, block_type, block_num,
                                 byref(data), byref(size))
        check_error(result, client=True)
        logger.info('received %s bytes' % size)

    def db_get(self, db_number):
        """Uploads a DB from AG.
        """
        logging.debug("db_get db_number: %s" % db_number)
        buffer_ = buffer_type()
        result = clib.Cli_DBGet(self.pointer, db_number, byref(buffer_),
                                  byref(c_int(buffer_size)))
        check_error(result, client=True)
        return bytearray(buffer_)

    def read_area(self, area, dbnumber, start, amount, wordlen):
        """This is the main function to read data from a PLC.
        With it you can read DB, Inputs, Outputs, Merkers, Timers and Counters.
        """
        logging.debug("reading area: %s dbnumber: %s start: %s: amount %s: "
                      "wordlen: %s" % (area, dbnumber, start, amount, wordlen))
        data = (wordlen_to_ctypes[wordlen] * amount)()
        result = clib.Cli_ReadArea(self.pointer, area, dbnumber, start, amount,
                                   wordlen, byref(data))
        check_error(result, client=True)
        return data

    @error_wrap
    def write_area(self, area, dbnumber, start, amount, wordlen, data):
        """This is the main function to write data into a PLC. It's the
        complementary function of Cli_ReadArea(), the parameters and their
        meanings are the same. The only difference is that the data is
        transferred from the buffer pointed by pUsrData into PLC.
        """
        logging.debug("writing area: %s dbnumber: %s start: %s: amount %s: "
              "wordlen: %s" % (area, dbnumber, start, amount, wordlen))
        return clib.Cli_WriteArea(self.pointer, area, dbnumber, start, amount,
                                  wordlen, byref(data))

    def list_blocks(self):
        """Returns the AG blocks amount divided by type.

        :returns: a snap7.types.BlocksList object.
        """
        logging.debug("listing blocks")
        blocksList = BlocksList()
        result = clib.Cli_ListBlocks(self.pointer, byref(blocksList))
        check_error(result, client=True)
        logging.debug("blocks: %s" % blocksList)
        return blocksList

    @error_wrap
    def set_session_password(self, password):
        """Send the password to the PLC to meet its security level."""
        assert len(password) <= 8, 'maximum password length is 8'
        return clib.Cli_SetSessionPassword(self.pointer, c_char_p(password))

    @error_wrap
    def clear_session_password(self):
        """Clears the password set for the current session (logout)."""
        return clib.Cli_ClearSessionPassword(self.pointer)

"""
Cli_ABRead
Cli_ABWrite
Cli_AsABRead
Cli_AsABWrite
Cli_AsCompress
Cli_AsCopyRamToRom
Cli_AsCTRead
Cli_AsCTWrite
Cli_AsDBFill
Cli_AsDBGet
Cli_AsDBRead
Cli_AsDBWrite
Cli_AsDownload
Cli_AsEBRead
Cli_AsEBWrite
Cli_AsFullUpload
Cli_AsListBlocksOfType
Cli_AsMBRead
Cli_AsMBWrite
Cli_AsReadArea
Cli_AsReadSZL
Cli_AsReadSZLList
Cli_AsTMRead
Cli_AsTMWrite
Cli_AsUpload
Cli_AsWriteArea
Cli_CheckAsCompletion
Cli_ClearSessionPassword
Cli_Compress
Cli_Connect
Cli_ConnectTo
Cli_CopyRamToRom
Cli_Create
Cli_CTRead
Cli_CTWrite
Cli_DBFill
Cli_DBGet
Cli_DBRead
Cli_DBWrite
Cli_Delete
Cli_Destroy
Cli_Disconnect
Cli_Download
Cli_EBRead
Cli_EBWrite
Cli_ErrorText
Cli_FullUpload
Cli_GetAgBlockInfo
Cli_GetCpInfo
Cli_GetCpuInfo
Cli_GetExecTime
Cli_GetLastError
Cli_GetOrderCode
Cli_GetParam
Cli_GetPduLength
Cli_GetPgBlockInfo
Cli_GetPlcDateTime
Cli_GetPlcStatus
Cli_GetProtection
Cli_IsoExchangeBuffer
Cli_ListBlocks
Cli_ListBlocksOfType
Cli_MBRead
Cli_MBWrite
Cli_PlcColdStart
Cli_PlcHotStart
Cli_PlcStop
Cli_ReadArea
Cli_ReadMultiVars
Cli_ReadSZL
Cli_ReadSZLList
Cli_SetAsCallback
Cli_SetParam
Cli_SetPlcDateTime
Cli_SetPlcSystemDateTime
Cli_SetSessionPassword
Cli_TMRead
Cli_TMWrite
Cli_Upload
Cli_WaitAsCompletion
Cli_WriteArea
Cli_WriteMultiVars
"""
