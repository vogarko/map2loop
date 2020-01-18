/******************************************************************************
* Different types used in ConverterLib.
*
* Author: Vitaliy Ogarko (2016).
*******************************************************************************/

#ifndef converter_types_h
#define converter_types_h

#include <vector>
#include <map>
#include <string>

#include "converter_utils.h"
#include "bounding_box.h"
#include "clipper.hpp"

using ClipperLib::Paths;

namespace ConverterLib {

// Fault or multi-polygon or point.
class Object
{
public:
  // Unique id.
  int id;
  // Min/max age ma (for polygons).
  int min_age, max_age;
  // Unit name (for polygons).
  std::string name;
  // Group name (for polygons).
  std::string group;
  // ENGUINT code (for polygons).
  std::string code;
  // Description (for polygons).
  std::string description;
  // Rocktypes (for polygons).
  std::string rocktype1, rocktype2;
  // Dip and dip direction (for points).
  int dip, dip_dir;
  // Polygons withing a multi-polygon, or a fault, or point coordinates.
  Paths paths;
  // Bounding box (AABB), Y-axis points down.
  AABB aabb;

  Object(AABB _aabb = AABB(0)):
         aabb(_aabb) {};
};

enum ContactType { StratigraphicContact, FaultContact, MixedContact, NotSpecifiedContact };

// Litho contact between two polygons.
class Contact
{
public:
  // Unique contact id.
  int id;
  // Pointers to polygons that share a contact.
  const Object *obj1, *obj2;
  // Coordinates of vertexes.
  Path path;
  // The contact length (in meters).
  double length;
  // Contact type.
  ContactType type;

  Contact(int _id = - 1):
          id(_id) {};

  bool operator< (const Contact &other) const
  {
    return id < other.id;
  }
};

// Class representing a geological unit.
class Unit
{
public:
  // Unique id only within a local (clipped) map.
  int id;
  // Unit name (unique identifier).
  std::string name;
  // Group name.
  std::string group;
  // ENGUINT codes of polygons that share this unit.
  std::vector<std::string> codes;
  // Perimeter length (total length of all polygon segments that belong to this unit).
  double length;
  // Min/max age (ma).
  double min_age, max_age;
  // A flag for sill-units.
  bool is_sill;
  // Rocktypes.
  std::string rocktype1, rocktype2;

  bool operator< (const Unit &other) const
  {
    return length < other.length;
  }
};

typedef std::vector<Contact> Contacts;

// Litho contact between two units.
class UnitContact
{
public:
  // Units that are in contact.
  // (To make them pointers, need to add a container of all units in the map).
  Unit unit1, unit2;
  // Polygon contacts which the unit contact is made of.
  Contacts contacts;
  // Total contact length, length of fault, stratigraphic and mixed contacts.
  double total_length, faults_length, stratigraphic_length, mixed_length;
  // Relative contact length w.r.t. (average) unit length.
  double relative_length;
  // Contact type.
  ContactType type;
  // Flags for igneous contacts;
  bool isIgneous;
  bool isIntrusiveIgneous;
};

typedef std::vector<Object> Objects;
// Container of units in the clipped map (not all map units stored).
typedef std::map<std::string, Unit> Units;
typedef std::vector<UnitContact> UnitContacts;
typedef std::map<std::string, int> Groups;

}

#endif
