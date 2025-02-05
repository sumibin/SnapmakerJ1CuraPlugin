from io import StringIO
from typing import TYPE_CHECKING, List, Optional

from cura.PrinterOutput.PrinterOutputDevice import ConnectionState
from UM.FileHandler.WriteFileJob import WriteFileJob
from UM.Mesh.MeshWriter import MeshWriter
from UM.Message import Message

from ..gcode_writer.SnapmakerGCodeWriter import SnapmakerGCodeWriter
from .SACPNetworkedPrinterOutputDevice import SACPNetworkedPrinterOutputDevice

if TYPE_CHECKING:
    from UM.FileHandler.FileHandler import FileHandler
    from UM.Scene.SceneNode import SceneNode


class SnapmakerArtisanOutputDevice(SACPNetworkedPrinterOutputDevice):

    def requestWrite(self, nodes: List["SceneNode"], file_name: Optional[str] = None,
                     limit_mimetypes: bool = False, file_handler: Optional["FileHandler"] = None,
                     filter_by_machine: bool = False, **kwargs) -> None:
        if self.connectionState == ConnectionState.Busy:
            Message(title="Unable to send request",
                    text="Machine {} is busy".format(self.getId())).show()
            return

        self.writeStarted.emit(self)

        message = Message(
            text="Preparing to upload",
            progress=-1,
            lifetime=0,
            dismissable=False,
            use_inactivity_timer=False,
        )
        message.show()

        self._stream = StringIO()  # create a new io stream

        writer = SnapmakerGCodeWriter()
        writer.setExtruderMode("Normal")

        job = WriteFileJob(writer, self._stream, nodes, MeshWriter.OutputMode.TextMode)
        job.finished.connect(self._writeFileJobFinished)
        job.setMessage(message)
        job.start()
