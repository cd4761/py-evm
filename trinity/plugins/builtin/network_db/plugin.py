import asyncio
from argparse import (
    Namespace,
    ArgumentParser,
    _SubParsersAction,
)
import logging
from typing import Iterable

from eth_utils import to_tuple

from sqlalchemy.orm import Session

from p2p.service import BaseService
from p2p.tracking.connection import (
    BaseConnectionTracker,
    NoopConnectionTracker,
)

from trinity._utils.shutdown import (
    exit_with_service_and_endpoint,
)
from trinity.config import (
    TrinityConfig,
)
from trinity.db.orm import get_tracking_database
from trinity.extensibility.plugin import (
    BaseIsolatedPlugin,
)
from trinity.db.network import (
    get_networkdb_path,
)
from trinity.endpoint import (
    TrinityEventBusEndpoint,
)

from .connection.server import ConnectionTrackerServer
from .connection.tracker import (
    SQLiteConnectionTracker,
    MemoryConnectionTracker,
)
from .cli import (
    TrackingBackend,
    NormalizeTrackingBackend,
)


class NetworkDBPlugin(BaseIsolatedPlugin):
    # we access this logger from a classmethod so it needs to be available on
    # the class (instead of as a computed property like the base class
    # provided.
    logger = logging.getLogger(f'trinity.extensibility.plugin.NetworkDBPlugin')

    @property
    def name(self) -> str:
        return "Network Database"

    @property
    def normalized_name(self) -> str:
        return "network-db"

    def configure_parser(self, arg_parser: ArgumentParser, subparser: _SubParsersAction) -> None:
        tracking_parser = arg_parser.add_argument_group('network db')
        tracking_parser.add_argument(
            '--network-tracking-backend',
            help=(
                "Configure whether nodes are tracked and how. (sqlite3: persistent "
                "tracking across runs from an on-disk sqlite3 database, memory: tracking "
                "only in memory, do-not-track: no tracking)"
            ),
            action=NormalizeTrackingBackend,
            choices=('sqlite3', 'memory', 'do-not-track'),
            default=TrackingBackend.sqlite3,
            type=str,
        )
        tracking_parser.add_argument(
            '--disable-networkdb-plugin',
            help=(
                "Disables the builtin 'Networkt Database' plugin. "
                "**WARNING**: disabling this API without a proper replacement "
                "will cause your trinity node to crash."
            ),
            action='store_true',
        )
        tracking_parser.add_argument(
            '--disable-blacklistdb',
            help=(
                "Disables the blacklist database server component of the Network Database plugin."
                "**WARNING**: disabling this API without a proper replacement "
                "will cause your trinity node to crash."
            ),
            action='store_true',
        )

        # Command to wipe the on-disk database
        remove_db_parser = subparser.add_parser(
            'remove-network-db',
            help='Remove the on-disk sqlite database that tracks data about the p2p network',
        )
        remove_db_parser.set_defaults(func=self.clear_node_db)

    def on_ready(self, manager_eventbus: TrinityEventBusEndpoint) -> None:
        if self.context.args.disable_networkdb_plugin:
            self.logger.warning("Network Database disabled via CLI flag")
            # Allow this plugin to be disabled for extreme cases such as the
            # user swapping in an equivalent experimental version.
            return
        else:
            self.start()

    @classmethod
    def clear_node_db(cls, args: Namespace, trinity_config: TrinityConfig) -> None:
        db_path = get_networkdb_path(trinity_config)

        if db_path.exists():
            cls.logger.info("Removing network database at: %s", db_path.resolve())
            db_path.unlink()
        else:
            cls.logger.info("No network database found at: %s", db_path.resolve())

    _session: Session = None

    def _get_database_session(self) -> Session:
        if self._session is None:
            self._session = get_tracking_database(get_networkdb_path(self.context.trinity_config))
        return self._session

    def _get_blacklist_tracker(self) -> BaseConnectionTracker:
        backend = self.context.args.network_tracking_backend

        if backend is TrackingBackend.sqlite3:
            session = self._get_database_session()
            return SQLiteConnectionTracker(session)
        elif backend is TrackingBackend.memory:
            return MemoryConnectionTracker()
        elif backend is TrackingBackend.do_not_track:
            return NoopConnectionTracker()
        else:
            raise Exception(f"INVARIANT: {backend}")

    def _get_blacklist_service(self) -> ConnectionTrackerServer:
        tracker = self._get_blacklist_tracker()
        blacklist_service = ConnectionTrackerServer(
            event_bus=self.event_bus,
            tracker=tracker,
        )
        return blacklist_service

    @to_tuple
    def _get_services(self) -> Iterable[BaseService]:
        if self.context.args.disable_blacklistdb:
            # Allow this plugin to be disabled for extreme cases such as the
            # user swapping in an equivalent experimental version.
            self.logger.warning("Blacklist Database disabled via CLI flag")
        else:
            yield self._get_blacklist_service()

    def do_start(self) -> None:
        loop = asyncio.get_event_loop()

        tracker_services = self._get_services()

        for service in tracker_services:
            asyncio.ensure_future(exit_with_service_and_endpoint(service, self.event_bus))
            asyncio.ensure_future(service.run())

        loop.run_forever()
        loop.close()
